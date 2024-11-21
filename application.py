from flask import Flask, request, render_template, send_file
import base64
import io
import os
from PIL import Image
import random  

app = Flask(__name__)

# Serve the HTML template
@app.route('/')
def upload_form():
    return render_template('index.html')

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
