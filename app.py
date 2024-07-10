from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse, parse_qs
import json

app = Flask(__name__)

data = []

def get_unique_id(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path.split('/')[-1].split('.')[0]

@app.route('/', methods=['GET'])
def index():
    links = [f"/image/{get_unique_id(item['image_url'])}" for item in data]
    return render_template('index.html', links=links)

@app.route('/image/<unique_id>', methods=['GET'])
def image_page(unique_id):
    for item in data:
        if get_unique_id(item['image_url']) == unique_id:
            return render_template('image.html', item=item)
    return "Image not found", 404

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        new_data = request.json
        if isinstance(new_data, dict):
            # If we receive a single object
            data.append(new_data)
        elif isinstance(new_data, list):
            # If we receive a list of objects
            data.extend(new_data)
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
        return jsonify({"status": "success", "message": "Data received"}), 200

if __name__ == '__main__':
    app.run(debug=True)