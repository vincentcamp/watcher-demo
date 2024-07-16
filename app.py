from flask import Flask, render_template, request, jsonify, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
import logging
import json

app = Flask(__name__, static_folder='.', static_url_path='')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB Atlas connection
MONGODB_URI = os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    logger.error("MONGODB_URI is not set in environment variables")
    raise ValueError("MONGODB_URI environment variable is not set")

try:
    # Use a non-SRV URI if possible
    if MONGODB_URI.startswith('mongodb+srv://'):
        logger.warning("SRV URI detected. Attempting to use non-SRV URI.")
        MONGODB_URI = MONGODB_URI.replace('mongodb+srv://', 'mongodb://')
    
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # This will raise an exception if the connection fails
    db = client['watcher_db']
    collection = db['images']
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    logger.error("If using SRV URI, ensure dnspython is installed: pip install dnspython")
    raise

def standardize_data(item):
    """Standardize the data format to match Image 1 layout."""
    if isinstance(item, dict):
        payload = item.get('payload', {})
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse payload JSON: {payload}")
                payload = {}
        
        timestamp = item.get('timestamp') or payload.get('timestamp')
        if timestamp and isinstance(timestamp, str):
            try:
                timestamp = int(float(timestamp))
            except ValueError:
                logger.error(f"Invalid timestamp format: {timestamp}")
                timestamp = None

        return {
            "_id": str(item.get('_id', ObjectId())),
            "tlid": payload.get('tlid') or item.get('tlid'),
            "tn": payload.get('tn') or item.get('tn'),
            "content": payload.get('content') or item.get('content'),
            "image_url": payload.get('image_url') or item.get('image_url'),
            "timestamp": timestamp,
            "formatted_timestamp": format_timestamp(timestamp),
            "orgId": payload.get('orgId') or item.get('orgId'),
            "eui": payload.get('eui') or item.get('eui'),
            "channel": payload.get('channel') or item.get('channel')
        }
    else:
        logger.error(f"Invalid item type: {type(item)}")
        return {}

def format_timestamp(timestamp):
    if timestamp:
        try:
            timestamp_seconds = timestamp / 1000.0
            dt_utc = datetime.utcfromtimestamp(timestamp_seconds)
            dt_china = dt_utc + timedelta(hours=8)
            return dt_china.strftime("%Y-%m-%d %H:%M:%S CST")
        except Exception as e:
            logger.error(f"Failed to format timestamp {timestamp}: {e}")
    return None

@app.route('/')
def index():
    try:
        items = list(collection.find())
        logger.debug(f"Retrieved {len(items)} items from the database")
        standardized_items = [standardize_data(item) for item in items]
        logger.debug(f"Standardized {len(standardized_items)} items")
        return render_template('index.html', items=standardized_items)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return "An error occurred", 500

@app.route('/<path:path>')
def static_proxy(path):
    logger.debug(f"Attempting to serve static file: {path}")
    try:
        return send_from_directory('.', path)
    except Exception as e:
        logger.error(f"Failed to serve static file {path}: {e}")
        return f"File not found: {path}", 404

@app.route('/api/image/<id>')
def image_page(id):
    try:
        item = collection.find_one({'_id': ObjectId(id)})
        if item:
            standardized_item = standardize_data(item)
            return render_template('image.html', item=standardized_item)
        return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        logger.error(f"Error in image_page route: {e}")
        return "An error occurred", 500

@app.route('/api/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        try:
            new_data = request.json
            standardized_data = standardize_data(new_data)
            result = collection.insert_one(standardized_data)
            return jsonify({"status": "success", "message": "Data received", "id": str(result.inserted_id)}), 200
        except Exception as e:
            logger.error(f"Error in receive_data route: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/test')
def test():
    try:
        items = list(collection.find())
        standardized_items = [standardize_data(item) for item in items]
        return jsonify(standardized_items)
    except Exception as e:
        logger.error(f"Error in test route: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug')
def debug():
    try:
        items = list(collection.find())
        standardized_items = [standardize_data(item) for item in items]
        return jsonify(standardized_items)
    except Exception as e:
        logger.error(f"Error in debug route: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Static folder is set to: {app.static_folder}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Contents of static folder: {os.listdir(app.static_folder)}")
    app.run(debug=True)