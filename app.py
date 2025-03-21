from flask import Flask, request, jsonify, send_file, render_template
import csv
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "gcodes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

SHOPIFY_API_KEY = "your_shopify_api_key"
SHOPIFY_PASSWORD = "your_shopify_password"
SHOPIFY_STORE_NAME = "your_shopify_store"

def generate_gcode(name, message):
    gcode = f"""
    G21 ; Set units to millimeters
    G90 ; Absolute positioning
    G0 X10 Y10 ; Move to start position
    G1 X20 Y20 F1000 ; Start writing
    ; Writing text: {message}
    G0 X0 Y0 ; Return to origin
    """
    return gcode.strip()

@app.route('/')
def index():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return process_csv(filepath)

def process_csv(filepath):
    gcode_files = []
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            name = row[0]
            message = f"Hey {name}, thanks for shopping with us!"
            gcode = generate_gcode(name, message)
            gcode_filename = f"{name}.gcode"
            gcode_path = os.path.join(OUTPUT_FOLDER, gcode_filename)
            with open(gcode_path, 'w') as gfile:
                gfile.write(gcode)
            gcode_files.append(gcode_filename)
    return jsonify({"message": "G-code files generated", "files": gcode_files})

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/shopify', methods=['GET'])
def fetch_shopify_customers():
    url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2024-01/customers.json"
    response = requests.get(url, auth=(SHOPIFY_API_KEY, SHOPIFY_PASSWORD))
    if response.status_code == 200:
        customers = response.json().get("customers", [])
        names = [customer.get("first_name", "") for customer in customers if "first_name" in customer]
        return jsonify({"customer_names": names})
    else:
        return jsonify({"error": "Failed to fetch customer data from Shopify"}), 400

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    data = request.get_json()
    user_input = data.get("message", "").lower()
    
    if "generate gcode" in user_input:
        return jsonify({"response": "Please upload a CSV file to generate G-code."})
    elif "shopify customers" in user_input:
        return fetch_shopify_customers()
    elif "help" in user_input:
        return jsonify({"response": "I can generate G-code, fetch Shopify customers, or provide assistance. Try 'Generate G-code' or 'Fetch Shopify Customers'."})
    else:
        return jsonify({"response": "I'm your AI assistant. Ask me to generate G-code, fetch Shopify customers, or get help."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
