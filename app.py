import os
import csv
from io import BytesIO
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import svgwrite
from hershey import HersheyFonts

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' # Ensure you have a folder named 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

hf = HersheyFonts()
default_hershey_font = 'gothiceng'
hf.load_default_font(default_hershey_font)

def text_to_stroke_svg_path_hershey(text, font_name=default_hershey_font, scale=1.5, x_offset=0, y_offset=70):
"""Converts text to SVG path data using Hershey fonts."""
hf.load_default_font(font_name)
path_data = ""
current_x = x_offset
for char in text:
glyph = hf.char_to_glyph(char)
if glyph:
for stroke in glyph.strokes:
for i in range(len(stroke) - 1):
x1, y1 = stroke[i]
x2, y2 = stroke[i+1]
path_data += f"M{current_x + x1 * scale},{y_offset + y1 * scale} L{current_x + x2 * scale},{y_offset + y2 * scale} "
current_x += glyph.width * scale
else:
current_x += 10 * scale
return path_data.strip()

@app.route('/', methods=)
def index():
if request.method == 'POST':
if 'csv_file' not in request.files:
return render_template('index.html', error='No file part', fonts=hf.default_font_names)
file = request.files['csv_file']
if file.filename == '':
return render_template('index.html', error='No selected file', fonts=hf.default_font_names)
if file:
filename = secure_filename(file.filename)
filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
file.save(filepath)
message_template = request.form['message']
font_choice = request.form.get('font', default_hershey_font)
svg_files = generate_personalized_svg(filepath, message_template, font_choice)
return render_template('download.html', svg_files=svg_files)
return render_template('index.html', fonts=hf.default_font_names)

def generate_personalized_svg(csv_filepath, message_template, font_choice):
"""Reads names from CSV and generates personalized SVG files using Hershey fonts."""
svg_files_info =
with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
reader = csv.DictReader(csvfile)
for row in reader:
first_name = row.get('First Name')
if first_name:
personalized_message = message_template.replace('[First Name]', first_name)
svg_filename = f"{first_name.lower()}_note.svg"
svg_filepath = os.path.join(app.config['UPLOAD_FOLDER'], svg_filename)
create_stroke_svg_hershey(personalized_message, svg_filepath, font_choice)
svg_files_info.append({'filename': svg_filename, 'filepath': svg_filepath})
return svg_files_info

def create_stroke_svg_hershey(text, output_path, font_choice):
"""Creates an SVG file with the given text as stroke-based paths using Hershey fonts."""
dwg = svgwrite.Drawing(output_path, width=300, height=100)
path_data = text_to_stroke_svg_path_hershey(text, font_choice)
path = dwg.path(d=path_data, fill='none', stroke='black', stroke_width=1)
dwg.add(path)
dwg.save()

@app.route('/download/<filename>')
def download_file(filename):
"""Downloads the specified SVG file."""
return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),
mimetype='image/svg+xml',
as_attachment=True)

if __name__ == '__main__':
app.run(debug=True)
