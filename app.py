from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import pandas as pd
import zipfile, os, shutil
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.font_manager import FontProperties

app = Flask(__name__)
app.secret_key = 'secretkey123'

UPLOAD_FOLDER = 'uploads'
SVG_FOLDER = 'svgs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SVG_FOLDER, exist_ok=True)

def text_to_svg(text, filename):
    fig, ax = plt.subplots()
    ax.axis('off')

    font = FontProperties(family="Arial", size=20, weight="bold")
    text_path = TextPath((0, 0), text, prop=font)
    patch = PathPatch(text_path, facecolor='black', lw=0)
    ax.add_patch(patch)

    ax.set_xlim(text_path.get_extents().xmin - 10, text_path.get_extents().xmax + 10)
    ax.set_ylim(text_path.get_extents().ymin - 10, text_path.get_extents().ymax + 10)
    ax.set_aspect('equal')

    plt.savefig(filename, format='svg', bbox_inches='tight', pad_inches=0)
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    columns = []
    if request.method == 'POST':
        file = request.files['csv_file']
        if file.filename == '':
            flash('Please select a CSV file.')
            return redirect(url_for('index'))

        csv_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(csv_path)

        df = pd.read_csv(csv_path)
        columns = df.columns.tolist()
        
        return render_template('index.html', columns=columns, csv_uploaded=True, csv_filename=file.filename)

    return render_template('index.html', columns=columns, csv_uploaded=False)

@app.route('/generate', methods=['POST'])
def generate():
    csv_filename = request.form['csv_filename']
    column_name = request.form['column_name']
    message_template = request.form['message_template']

    csv_path = os.path.join(UPLOAD_FOLDER, csv_filename)
    df = pd.read_csv(csv_path)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session_folder = os.path.join(SVG_FOLDER, f'svgs_{timestamp}')
    os.makedirs(session_folder, exist_ok=True)

    for value in df[column_name]:
        safe_value = str(value).replace("/", "_").replace("\\", "_")
        svg_path = os.path.join(session_folder, f"{safe_value}.svg")
        personalized_message = message_template.replace(f"[{column_name}]", str(value))
        text_to_svg(personalized_message, svg_path)

    zip_filename = f'svgs_{timestamp}.zip'
    zip_path = os.path.join(SVG_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zf:
        for svg_file in os.listdir(session_folder):
            zf.write(os.path.join(session_folder, svg_file), svg_file)

    shutil.rmtree(session_folder)
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

