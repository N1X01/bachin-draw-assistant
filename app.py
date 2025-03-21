from flask import Flask, request, render_template, send_file
import csv
import os
import uuid
import zipfile
from io import TextIOWrapper
from jinja2 import Template

app = Flask(__name__)
UPLOAD_FOLDER = "generated_svgs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SVG_TEMPLATE = """<?xml version="1.0" standalone="no"?>
<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
  <text x="50%" y="50%" font-size="28" text-anchor="middle" fill="black" font-family="Arial, sans-serif">
    {{ message }}
  </text>
</svg>"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        csv_file = request.files["csv"]
        message_template = request.form["message"]
        temp_folder = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()))
        os.makedirs(temp_folder, exist_ok=True)

        reader = csv.DictReader(TextIOWrapper(csv_file, encoding="utf-8"))
        for row in reader:
            name = row.get("First Name", "Customer").strip()
            personalized_message = message_template.replace("[First Name]", name)
            svg_content = Template(SVG_TEMPLATE).render(message=personalized_message)
            with open(os.path.join(temp_folder, f"{name}.svg"), "w", encoding="utf-8") as f:
                f.write(svg_content)

        zip_filename = f"{temp_folder}.zip"
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for root, _, files in os.walk(temp_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), file)

        return send_file(zip_filename, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)

