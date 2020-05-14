import os
import config
from flask import Flask, request, jsonify, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from random import choice
from string import ascii_letters

app = Flask(__name__)
config = config.Config()

app.secret_key = config.get('secret_key')
API_KEY = config.get('api_key')
ALLOWED_EXTENSIONS = config.get('allowed_extensions')
UPLOAD_FOLDER = config.get('upload_folder')

def need_api_key(func):
	def wrapper(*args, **kwargs):
		if request.headers.get('X-API-Key') == API_KEY:
			return func(*args, **kwargs)
		else:
			abort(401)
	return wrapper

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(extension, path=UPLOAD_FOLDER):
	filename = ''.join(choice(ascii_letters) for i in range(6))

	while os.path.exists(os.path.join(path, "{}.{}".format(filename, extension))):
		filename = ''.join(choice(ascii_letters) for i in range(6))
	
	return filename

@app.route('/upload', methods=['POST'])
@need_api_key
def upload_file():
	if 'file' not in request.files:
		resp = jsonify({'message': 'File not included in the request'})
		resp.status_code = 400
		return resp

	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message': 'No file selected for uploading'})
		resp.status_code = 400
		return resp

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename.lower()).rsplit('.', 1)

		file.filename = "{}.{}".format(generate_filename(filename[1]), filename[1])
		file.save(os.path.join(UPLOAD_FOLDER, file.filename))
		
		resp = jsonify({'url': url_for('uploaded_file', filename=file.filename)})
		resp.status_code = 201
		return resp

	else:
		message = "Allowed file types: {}".format(", ".join(ALLOWED_EXTENSIONS))

		resp = jsonify({'message': message})
		resp.status_code = 400
		return resp

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run()