from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection
MONGODB_URI = os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    logger.error("MONGODB_URI is not set in environment variables")
    raise ValueError("MONGODB_URI environment variable is not set")

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client['watcher_db']
    collection = db['images']
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

def standardize_data(item):
    """Standardize the data format to match Image 1 layout."""
    if 'payload' in item:
        payload = item['payload']
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        return {
            "_id": item.get('_id', str(ObjectId())),
            "tlid": payload.get('tlid'),
            "tn": payload.get('tn'),
            "content": payload.get('content'),
            "image_url": payload.get('image_url'),
            "timestamp": payload.get('timestamp'),
            "orgId": payload.get('orgId'),
            "eui": payload.get('eui'),
            "channel": payload.get('channel')
        }
    else:
        return {
            "_id": item.get('_id', str(ObjectId())),
            "tlid": item.get('tlid'),
            "tn": item.get('tn'),
            "content": item.get('content'),
            "image_url": item.get('image_url'),
            "timestamp": item.get('timestamp'),
            "orgId": item.get('orgId'),
            "eui": item.get('eui'),
            "channel": item.get('channel')
        }

@app.route('/', methods=['GET'])
def index():
    items = list(collection.find())
    standardized_items = [standardize_data(item) for item in items]
    links = [f"/image/{str(item['_id'])}" for item in standardized_items]
    return render_template('index.html', links=links, items=standardized_items)

@app.route('/image/<id>', methods=['GET'])
def image_page(id):
    item = collection.find_one({'_id': ObjectId(id)})
    if item:
        standardized_item = standardize_data(item)
        return render_template('image.html', item=standardized_item, particle_text=standardized_item.get('content', ''))
    return "Image not found", 404

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        new_data = request.json
        standardized_data = standardize_data(new_data)
        result = collection.insert_one(standardized_data)
        return jsonify({"status": "success", "message": "Data received", "id": str(result.inserted_id)}), 200

@app.route('/test', methods=['GET'])
def test():
    items = list(collection.find())
    standardized_items = [standardize_data(item) for item in items]
    return jsonify(standardized_items)

@app.route('/debug')
def debug():
    items = list(collection.find())
    standardized_items = [standardize_data(item) for item in items]
    return jsonify(standardized_items)

if __name__ == '__main__':
    app.run(debug=True)