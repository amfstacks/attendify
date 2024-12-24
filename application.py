from flask import Flask, request, render_template, send_file, redirect, url_for, jsonify, flash
import base64
import io
import os
from PIL import Image
import random
import json

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Replace with a secure key in production

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGIONS_FILE = os.path.join(BASE_DIR, 'regions.json')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
TEMPLATE_IMAGE = os.path.join(STATIC_DIR, 'template.png')

# Ensure necessary directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

# Initialize regions.json if it doesn't exist
if not os.path.exists(REGIONS_FILE):
    with open(REGIONS_FILE, 'w') as f:
        json.dump([], f, indent=4)

# Admin Interface
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Handle base image upload
        base_image = request.files.get('base_image')
        if base_image:
            base_image.save(TEMPLATE_IMAGE)
            flash('Base image uploaded successfully!', 'success')

        # Handle regions data
        regions_data = request.form.get('regions')
        if regions_data:
            try:
                regions = json.loads(regions_data)
                if len(regions) > 1:
                    flash('Only one region is allowed. Please define exactly one region.', 'danger')
                else:
                    with open(REGIONS_FILE, 'w') as f:
                        json.dump(regions, f, indent=4)
                    flash('Region saved successfully!', 'success')
            except json.JSONDecodeError:
                flash('Invalid JSON data for regions.', 'danger')

        return redirect(url_for('admin'))

    # Load existing regions
    try:
        with open(REGIONS_FILE, 'r') as f:
            regions = json.load(f)
    except json.JSONDecodeError:
        regions = []
        flash('regions.json contains invalid JSON. Resetting to empty.', 'danger')
        with open(REGIONS_FILE, 'w') as f:
            json.dump(regions, f, indent=4)

    return render_template('admin.html', regions=regions)

# User Interface
@app.route('/')
def index():
    return render_template('index.html')

# Save Composite Design
@app.route('/save', methods=['POST'])
def save_design():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data provided.'}), 400

    try:
        # Decode the base64 image
        image_data = data['image'].split(",")[1]
        decoded_image = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(decoded_image)).convert("RGBA")

        # Generate a random filename
        random_filename = f"{random.randint(100000, 999999)}.png"
        save_path = os.path.join(PUBLIC_DIR, random_filename)

        # Save the image
        image.save(save_path)

        # Send the image as a downloadable file
        return send_file(save_path, mimetype='image/png', as_attachment=True, download_name='attendify_design.png')
    except Exception as e:
        print(f"Error saving design: {e}")
        return jsonify({'error': 'Failed to save the design.'}), 500

# Serve regions.json
@app.route('/regions.json')
def get_regions():
    try:
        with open(REGIONS_FILE, 'r') as f:
            regions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        regions = []
    return jsonify(regions)

if __name__ == '__main__':
    app.run(debug=True)
