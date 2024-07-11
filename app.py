from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse, parse_qs
import json
import uuid

app = Flask(__name__)

data = [{
    "_id": "668e5aea984117c9047caa2a",
    "tlid": 3,
    "tn": "Local Human Detection",
    "content": "human detected",
    "image_url": "https://sensecraft-statics.seeed.cc/mperdoidau/ZplS3rqt3akc7gIPRGmq/secret_AHCjazlbeB3PRSof.jpeg",
    "timestamp": 1720592406130,
    "orgId": 440599875707904,
    "eui": "2CF7F1C9627000A7",
    "channel": 1
}]

def get_unique_id(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path.split('/')[-1].split('.')[0]

@app.route('/', methods=['GET'])
def index():
    links = [f"/image/{item['_id']}" for item in data]
    return render_template('index.html', links=links)

@app.route('/image/<id>', methods=['GET'])
def image_page(id):
    for item in data:
        if item['_id'] == id:
            return render_template('image.html', item=item, particle_text=item.get('content', ''))
    return "Image not found", 404

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        new_data = request.json
        if isinstance(new_data, dict):
            # If we receive a single object
            new_data['_id'] = str(uuid.uuid4())  # Generate a new UUID for the item
            data.append(new_data)
            return jsonify({"status": "success", "message": "Data received", "id": new_data['_id']}), 200
        elif isinstance(new_data, list):
            # If we receive a list of objects
            for item in new_data:
                item['_id'] = str(uuid.uuid4())  # Generate a new UUID for each item
            data.extend(new_data)
            return jsonify({"status": "success", "message": "Data received", "ids": [item['_id'] for item in new_data]}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400

@app.route('/test', methods=['GET'])
def test():
    return jsonify(data)

@app.route('/debug')
def debug():
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)