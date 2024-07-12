from flask import Flask, render_template, request, jsonify, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
import logging
import json

app = Flask(__name__, static_folder='public')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
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
        
        standardized = {
            "_id": item.get('_id', str(ObjectId())),
            "tlid": payload.get('tlid'),
            "tn": payload.get('tn'),
            "content": payload.get('content'),
            "image_url": payload.get('image_url'),
            "timestamp": item.get('timestamp') or payload.get('timestamp'),
            "formatted_timestamp": format_timestamp(item.get('timestamp') or payload.get('timestamp')),
            "orgId": payload.get('orgId'),
            "eui": payload.get('eui'),
            "channel": payload.get('channel')
        }
    else:
        standardized = {
            "_id": item.get('_id', str(ObjectId())),
            "tlid": item.get('tlid'),
            "tn": item.get('tn'),
            "content": item.get('content'),
            "image_url": item.get('image_url'),
            "timestamp": item.get('timestamp'),
            "formatted_timestamp": format_timestamp(item.get('timestamp')),
            "orgId": item.get('orgId'),
            "eui": item.get('eui'),
            "channel": item.get('channel')
        }
    
    return standardized
    
def format_timestamp(timestamp):
    if timestamp:
        timestamp_seconds = timestamp / 1000.0
        dt_utc = datetime.utcfromtimestamp(timestamp_seconds)
        dt_china = dt_utc + timedelta(hours=8)
        return dt_china.strftime("%Y-%m-%d %H:%M:%S CST")
    return None

@app.route('/')
def index():
    logger.debug(f"Serving index.html from {app.static_folder}")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    logger.debug(f"Attempting to serve static file: {path}")
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        logger.error(f"Failed to serve static file {path}: {e}")
        return f"File not found: {path}", 404

@app.route('/api/', methods=['GET'])
def api_index():
    items = list(collection.find())
    standardized_items = [standardize_data(item) for item in items]
    links = [f"/image/{str(item['_id'])}" for item in standardized_items]
    return jsonify({'links': links, 'items': standardized_items})

@app.route('/api/image/<id>', methods=['GET'])
def image_page(id):
    item = collection.find_one({'_id': ObjectId(id)})
    if item:
        standardized_item = standardize_data(item)
        return jsonify(standardized_item)
    return jsonify({"error": "Image not found"}), 404

@app.route('/api/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        new_data = request.json
        standardized_data = standardize_data(new_data)
        result = collection.insert_one(standardized_data)
        return jsonify({"status": "success", "message": "Data received", "id": str(result.inserted_id)}), 200

@app.route('/api/test', methods=['GET'])
def test():
    items = list(collection.find())
    standardized_items = [standardize_data(item) for item in items]
    return jsonify(standardized_items)

@app.route('/api/debug')
def debug():
    items = list(collection.find())
    standardized_items = [standardize_data(item) for item in items]
    return jsonify(standardized_items)

if __name__ == '__main__':
    logger.info(f"Static folder is set to: {app.static_folder}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Contents of static folder: {os.listdir(app.static_folder)}")
    app.run(debug=True)