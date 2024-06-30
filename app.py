from contextlib import redirect_stdout
from io import StringIO
from flask import Flask, request, jsonify
import subprocess
import os
import img2gcode as img2gcode

# Configure file upload settings (adjust as needed)
UPLOAD_FOLDER = 'uploads'  # Folder to save uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
port = 55011


class PythonRunner:
    __globals = {}
    __locals = {}

    def run(self, code):
        f = StringIO()
        with redirect_stdout(f):
            exec(code, self.__globals, self.__locals)
        return f.getvalue()


pr = PythonRunner()


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def home():
    return 'Welcome! This private app is a service for converting images to gcode.'


def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/gcode", methods=["POST"])
def gcode():
    print("wow")
    print("files:")
    print(request.files)
    print("form:")
    print(request.form)
    print("path:")
    print(request.values)
    if 'image' not in request.files:
        return jsonify({'error': 'No image file sent'}), 400
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No selected image'}), 400
    print("wow2")

    if image_file and allowed_file(image_file.filename):
        print("wow3")
        # Generate a unique filename to avoid conflicts
        filename = f"image.{image_file.filename.rsplit('.', 1)[1]}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the image to the server
        image_file.save(image_path)
        try:
            arguments = ["python3", "img2gcode.py", "--file", filename, "--simplify", "2", "--threshold", "80"]
            subprocess.run(arguments)
            with open(f"{filename}.img2gcode/image.gc", "r") as file:
                lines = file.readlines()
                lines = [line.rstrip() for line in lines]
            return jsonify({"data": lines})
        except Exception as e:
            return jsonify({"error": e})
    else:
        print("wow4")
        return jsonify({"error": "Error, image not found."})


app.run(port=port)
