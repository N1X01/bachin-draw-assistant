import os
import csv
import subprocess
from flask import Flask, render_template, request, send_file
from datetime import datetime

# Set up Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SVG_FOLDER = 'svgs'

# Make sure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SVG_FOLDER, exist_ok=True)

# Generate SVG using vpype and Hershey font
def create_svg_with_vpype(text, output_path, font="futural", size=20):
    command = f"""vpype text -f "{font}" -s {size} "{text}" linesimplify write "{output_path}" """
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("❌ Error creating SVG:", result.stderr.decode())
    else:
        print("✅ SVG generated:", output_path)

# Flask route for index
@app.route('/', methods=['GET', 'POST'])
def index():
    hershey_fonts = [
        "futural", "cursive", "scriptc", "gothiceng", "gothicger", "timesi",
        "romand", "rowmant", "astro", "greekc", "mathlow", "symbolic"
    ]

    if request.method == 'POST':
        # Get form inputs
        csv_file = request.files['csv_file']
        message_template = request.form['message']
        font = request.form.get('font', 'futural')

        # Save uploaded CSV
        csv_path = os.path.join(UPLOAD_FOLDER, csv_file.filename)
        csv_file.save(csv_path)

        output_files = []

        # Read CSV and generate SVG for each name
        with open(csv_path, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                first_name = row['First Name']
                personalized_message = message_template.replace("[First Name]", first_name)

                # Unique file name with timestamp
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{first_name}_{timestamp}.svg"
                svg_path = os.path.join(SVG_FOLDER, filename)

                # Generate SVG
                create_svg_with_vpype(personalized_message, svg_path, font=font, size=20)
                output_files.append(svg_path)

        # Return the first file for download (can be zipped later)
        return send_file(output_files[0], as_attachment=True)

    return render_template('index.html', fonts=hershey_fonts)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
