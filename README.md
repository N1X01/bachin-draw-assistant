# Bachin Draw Assistant

This Flask application generates stroke-based SVG files from a Shopify customer CSV. Each SVG is personalized with a custom message using Hershey fonts and can be sent to a Bachin plotter for writing notes.

## Setup

1. Install Python 3 and clone this repository.
2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server locally:
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5000`.

## Usage

1. Prepare a CSV with a `First Name` column.
2. Open the app in your browser and upload the CSV.
3. Enter a message template using `[First Name]` as the placeholder.
4. Choose a Hershey font and generate the SVG notes.
5. Download the generated files for use with your plotter.

## Deployment

The repository includes a `render.yaml` configuration for deploying on [Render](https://render.com). Render installs the requirements and starts the app with `python app.py`. Ensure the app binds to `0.0.0.0` and uses the port defined by the `PORT` environment variable when deploying.

## License

This project is distributed under the MIT License.
