import os
import csv
import shutil
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = 'secretkey123'

UPLOAD_FOLDER = 'uploads'
GCODE_FOLDER = 'gcodes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GCODE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'csv_file' not in request.files:
        flash('No CSV file uploaded.')
        return redirect(url_for('index'))

    csv_file = request.files['csv_file']
    if csv_file.filename == '':
        flash('No file selected.')
        return redirect(url_for('index'))

    message_template = request.form.get('message_template', '')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    session_folder = os.path.join(GCODE_FOLDER, f'gcodes_{timestamp}')
    os.makedirs(session_folder, exist_ok=True)

    filepath = os.path.join(UPLOAD_FOLDER, f'customers_{timestamp}.csv')
    csv_file.save(filepath)

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first_name = row.get('First Name') or row.get('first_name') or row.get('first name') or ''
            if not first_name:
                continue
            personalized_msg = message_template.replace('[First Name]', first_name)
            filename = f"{first_name}.gcode"
            gcode_path = os.path.join(session_folder, filename)
            with open(gcode_path, 'w', encoding='utf-8') as gcode_file:
                gcode_file.write(f"; G-code for {first_name}\n")
                gcode_file.write(f"G21 ; Set units to mm\n")
                gcode_file.write(f"G90 ; Absolute positioning\n")
                gcode_file.write(f"(MSG: {personalized_msg})\n")
                gcode_file.write(f"G0 X0 Y0\n")
                gcode_file.write(f"M2 ; End of program\n")

    zip_filename = f'gcodes_{timestamp}.zip'
    zip_path = os.path.join(GCODE_FOLDER, zip_filename)
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', session_folder)

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

