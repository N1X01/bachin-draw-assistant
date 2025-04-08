import os
import uuid
from flask import Flask, render_template, request, send_file
import pandas as pd
from zipfile import ZipFile
from svgwrite import Drawing

app = Flask(__name__)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        csv_file = request.files["csv_file"]
        message_template = request.form["message"]

        df = pd.read_csv(csv_file)

        zip_id = str(uuid.uuid4())
        zip_path = os.path.join(OUTPUT_DIR, f"{zip_id}.zip")

        with ZipFile(zip_path, "w") as zipf:
            for _, row in df.iterrows():
                name = row.get("Name") or row.get("name") or "Customer"
                message = message_template.replace("{name}", name)

                svg_filename = f"{name.replace(' ', '_')}.svg"
                gcode_filename = svg_filename.replace(".svg", ".gcode")
                svg_path = os.path.join(OUTPUT_DIR, svg_filename)
                gcode_path = os.path.join(OUTPUT_DIR, gcode_filename)

                # Create SVG with text
                dwg = Drawing(svg_path, profile='tiny', size=("210mm", "297mm"))
                dwg.add(dwg.text(message, insert=("10mm", "20mm"), font_size="12px", font_family="hershey"))
                dwg.save()

                # Convert to G-code using vpype
                os.system(f"vpype read '{svg_path}' linemerge linesort write -o '{gcode_path}'")

                zipf.write(gcode_path, arcname=gcode_filename)

                os.remove(svg_path)
                os.remove(gcode_path)

        return send_file(zip_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
