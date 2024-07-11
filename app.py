from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)

MONGODB_URI = os.environ.get('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.get_default_database()
collection = db.images

@app.route('/', methods=['GET'])
def index():
    items = list(collection.find())
    links = [f"/image/{str(item['_id'])}" for item in items]
    return render_template('index.html', links=links, items=items)

@app.route('/image/<id>', methods=['GET'])
def image_page(id):
    item = collection.find_one({'_id': ObjectId(id)})
    if item:
        return render_template('image.html', item=item, particle_text=item.get('content', ''))
    return "Image not found", 404

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        new_data = request.json
        if isinstance(new_data, dict):
            result = collection.insert_one(new_data)
            return jsonify({"status": "success", "message": "Data received", "id": str(result.inserted_id)}), 200
        elif isinstance(new_data, list):
            result = collection.insert_many(new_data)
            return jsonify({"status": "success", "message": "Data received", "ids": [str(id) for id in result.inserted_ids]}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400

@app.route('/test', methods=['GET'])
def test():
    items = list(collection.find())
    return jsonify([{**item, '_id': str(item['_id'])} for item in items])

@app.route('/debug')
def debug():
    debug_info = {
        "MONGODB_URI": MONGODB_URI.split('@')[1] if MONGODB_URI else "Not set",
        "Database": db.name,
        "Collection": collection.name,
        "Document Count": collection.count_documents({})
    }
    return jsonify(debug_info)

if __name__ == '__main__':
    app.run(debug=True)