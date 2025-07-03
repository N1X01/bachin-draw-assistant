# Bachin Draw Assistant

This Flask app generates personalized SVG files for the Bachin T‑A4 plotter. Upload a CSV with customer first names and provide a message template like:

```
Hi [First Name], thanks for your purchase!
```

Each row in the CSV is turned into an SVG drawing using Hershey fonts. Generated files can be downloaded from the app.

## Setup

1. Install Python 3.11 and create a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Visit `http://127.0.0.1:5000` in your browser.

## Usage

- Choose a Shopify-exported CSV containing a `First Name` column.
- Enter your message template and select a font.
- Submit to generate SVG files and download them from the results page.

The generated SVGs can be converted to G-code with tools like `vpype` if required.
