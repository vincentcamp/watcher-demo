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
    db = client.get_default_database()
    collection = db.images
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

@app.route('/', methods=['GET'])
def index():
    try:
        items = list(collection.find())
        links = [f"/image/{str(item['_id'])}" for item in items]
        return render_template('index.html', links=links, items=items)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return "An error occurred", 500

@app.route('/image/<id>', methods=['GET'])
def image_page(id):
    try:
        item = collection.find_one({'_id': ObjectId(id)})
        if item:
            return render_template('image.html', item=item, particle_text=item.get('content', ''))
        return "Image not found", 404
    except Exception as e:
        logger.error(f"Error in image_page route: {e}")
        return "An error occurred", 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        try:
            new_data = request.json
            if isinstance(new_data, dict):
                result = collection.insert_one(new_data)
                return jsonify({"status": "success", "message": "Data received", "id": str(result.inserted_id)}), 200
            elif isinstance(new_data, list):
                result = collection.insert_many(new_data)
                return jsonify({"status": "success", "message": "Data received", "ids": [str(id) for id in result.inserted_ids]}), 200
            else:
                return jsonify({"status": "error", "message": "Invalid data format"}), 400
        except Exception as e:
            logger.error(f"Error in receive_data route: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    try:
        items = list(collection.find())
        return jsonify([{**item, '_id': str(item['_id'])} for item in items])
    except Exception as e:
        logger.error(f"Error in test route: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/debug')
def debug():
    try:
        debug_info = {
            "MONGODB_URI": MONGODB_URI.split('@')[1] if MONGODB_URI else "Not set",
            "Database": db.name,
            "Collection": collection.name,
            "Document Count": collection.count_documents({})
        }
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Error in debug route: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal Server Error: {e}")
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True)