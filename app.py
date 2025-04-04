from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import pandas as pd
import zipfile, os, shutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey123'

UPLOAD_FOLDER = 'uploads'
GCODE_FOLDER = 'gcodes'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GCODE_FOLDER, exist_ok=True)

def text_to_gcode(message, filename):
    gcode = [
        "G21 ; Set units to mm",
        "G90 ; Absolute positioning",
        "G1 X10 Y10 F1000 ; Move to start",
        "M03 ; Pen down / Start writing",
        f"; Writing message: {message}",
        "G1 X10 Y15 ; Simulated line",
        "M05 ; Pen up / End",
        "G1 X0 Y0 ; Return to origin"
    ]
    with open(filename, "w") as f:
        f.write("\n".join(gcode))

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

        try:
            df = pd.read_csv(csv_path, on_bad_lines='skip')
            columns = df.columns.tolist()
            return render_template('index.html', columns=columns, csv_uploaded=True, csv_filename=file.filename)
        except Exception as e:
            return f"❌ CSV parsing error: {str(e)}"

    return render_template('index.html', columns=columns, csv_uploaded=False)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        csv_filename = request.form['csv_filename']
        column_name = request.form['column_name']
        message_template = request.form['message_template']

        csv_path = os.path.join(UPLOAD_FOLDER, csv_filename)
        df = pd.read_csv(csv_path, on_bad_lines='skip', sep=None, engine='python')

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        session_folder = os.path.join(GCODE_FOLDER, f'gcodes_{timestamp}')
        os.makedirs(session_folder, exist_ok=True)

        for value in df[column_name]:
            safe_value = str(value).replace("/", "_").replace("\\", "_")
            gcode_path = os.path.join(session_folder, f"{safe_value}.nc")
            personalized_message = message_template.replace(f"[{column_name}]", str(value))
            text_to_gcode(personalized_message, gcode_path)

        zip_filename = f'gcodes_{timestamp}.zip'
        zip_path = os.path.join(GCODE_FOLDER, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zf:
            for gcode_file in os.listdir(session_folder):
                zf.write(os.path.join(session_folder, gcode_file), gcode_file)

        shutil.rmtree(session_folder)
        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return f"❌ G-code generation error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)
