from flask import Flask, request, send_file, render_template_string
from PIL import Image, ImageOps, ImageDraw
import io

app = Flask(__name__)

# Path to your design template
TEMPLATE_PATH = "template.png"

@app.route('/')
def upload_form():
    # Simple HTML form for image upload
    return render_template_string('''
        <!doctype html>
        <title>Dynamic Image Uploader</title>
        <h1>Upload your picture</h1>
        <form method="POST" action="/process" enctype="multipart/form-data">
            <label for="user_image">Upload Image:</label>
            <input type="file" name="user_image" accept="image/*" required>
            <button type="submit">Generate Design</button>
        </form>
    ''')

@app.route('/process', methods=['POST'])
def process_image():
    # Get uploaded user image
    user_image_file = request.files['user_image']
    user_image = Image.open(user_image_file)

    # Open the design template
    template = Image.open(TEMPLATE_PATH)

    # Resize and crop user's image to fit the circular area
    circular_size = (450, 450)  # Size of the circle (width, height)
    user_image = ImageOps.fit(user_image, circular_size, method=Image.Resampling.LANCZOS)

    # Create a circular mask
    mask = Image.new("L", circular_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + circular_size, fill=255)

    # Apply the mask to make the image circular
    circular_user_image = Image.new("RGBA", circular_size)
    circular_user_image.paste(user_image, (0, 0), mask=mask)

    # Paste the circular image onto the template
    position = (615, 450)  # Position where the circle will appear (adjust as needed)
    template.paste(circular_user_image, position, mask=mask)

    # Save final image to a BytesIO buffer
    output = io.BytesIO()
    template.save(output, format="PNG")
    output.seek(0)

    # Return the final image to the user
    return send_file(output, mimetype='image/png', as_attachment=True, download_name='final_design.png')

if __name__ == '__main__':
    app.run(debug=True)
