from flask import Flask, request, render_template, send_file, redirect, url_for, jsonify
import base64
import io
import os
from PIL import Image
import random  
import json

app = Flask(__name__)

REGIONS_FILE = 'regions.json'

if not os.path.exists(REGIONS_FILE):
    with open(REGIONS_FILE, 'w') as f:
        json.dump([], f, indent=4)

# Serve the HTML template
@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Receive the base image and regions data
        base_image = request.files.get('base_image')
        regions_data = request.form.get('regions')

        if base_image:
            base_image_path = os.path.join('static', 'template.png')
            base_image.save(base_image_path)

        if regions_data:
            # Save regions data to a JSON file
            with open(REGIONS_FILE, 'w') as f:
                json.dump(json.loads(regions_data), f)

        return redirect(url_for('admin'))

    # Load existing regions if available
    regions = []
    if os.path.exists(REGIONS_FILE):
        with open(REGIONS_FILE, 'r') as f:
            regions = json.load(f)

    return render_template('admin.html', regions=regions)


@app.route('/regions.json')
def get_regions():
    REGIONS_FILE = 'regions.json'  # Ensure this path is correct
    if os.path.exists(REGIONS_FILE):
        try:
            with open(REGIONS_FILE, 'r') as f:
                regions = json.load(f)
        except json.JSONDecodeError:
            regions = []
            print("Error: regions.json contains invalid JSON.")
    else:
        regions = []
        print("Warning: regions.json does not exist. Initializing with empty list.")
        with open(REGIONS_FILE, 'w') as f:
            json.dump(regions, f, indent=4)
    return jsonify(regions)

# Save the final design from the canvas
@app.route('/save', methods=['POST'])
def save_design():
    data = request.get_json()
    image_data = data['image'].split(",")[1]  # Remove the data:image/png;base64 prefix
    decoded_image = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(decoded_image))
    
    # # Save the final image
    # output_path = "final_design.png"
    # image.save(output_path)

    # # Return the saved image as a response
    # return send_file(output_path, mimetype='image/png', as_attachment=True)
    random_filename = f"{random.randint(100000, 999999)}.png"
    save_path = os.path.join("public", random_filename)

    # Ensure the directory exists
    os.makedirs("public", exist_ok=True)
    
    # Save the image to the server
    image.save(save_path)

    # Save the image to a BytesIO buffer for download
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(save_path, mimetype='image/png', as_attachment=True)


if __name__ == '__main__':
    app.run()
