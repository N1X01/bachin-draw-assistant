from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from zipfile import ZipFile
import uuid

app = Flask(__name__)

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message_template = request.form["message"]
        csv_file = request.files["csv_file"]
        df = pd.read_csv(csv_file)
        zip_filename = f"{uuid.uuid4()}.zip"
        zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)

        with ZipFile(zip_path, "w") as zipf:
            for i, row in df.iterrows():
                name = row["Name"]
                message = message_template.replace("{name}", name)
                filename = f"{name.replace(' ', '_')}.gcode"
                gcode_content = generate_gcode(message)
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                with open(filepath, "w") as f:
                    f.write(gcode_content)
                zipf.write(filepath, arcname=filename)
                os.remove(filepath)

        return send_file(zip_path, as_attachment=True)

    return render_template("index.html")

def generate_gcode(message):
    # Simulate G-code output (replace with actual generation logic if needed)
    return f"; G-code for: {message}\nG28 ; Home\nG1 X10 Y10\n; ... more G-code here ...\n"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
