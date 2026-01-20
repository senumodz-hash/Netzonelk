from flask import Flask, render_template, jsonify, request, redirect
from flask_cors import CORS
from functools import wraps
import json
import os
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# =========================
# CONFIGURATION
# =========================
PUBLIC_KEY = "NZ_PUB_7f9a2e8c4b6d1a5f3e0c9b7a4d2f8e1c"
SECRET_KEY_FILE = "static/data/secret_key.txt"

# MongoDB setup
MONGO_USER = "senumodz_db_user"
MONGO_PASS = "fjjfx6apE5wVNI7I"
MONGO_DB = "NetzoneDB"
MONGO_HOST = "localhost"
MONGO_PORT = 27017

client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin")
db = client[MONGO_DB]

# =========================
# UTILITY FUNCTIONS
# =========================
def load_json(filename):
    filepath = os.path.join('static/data', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_secret_key():
    try:
        with open(SECRET_KEY_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def require_api_keys(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        public_key = request.args.get('public_key') or request.headers.get('X-Public-Key')
        secret_key = request.args.get('secret_key') or request.headers.get('X-Secret-Key')
        stored_secret = get_secret_key()

        if not public_key or not secret_key:
            return jsonify({'error': 'Missing API keys', 'message': 'Both keys required'}), 401

        if public_key != PUBLIC_KEY or secret_key != stored_secret:
            return jsonify({'error': 'Invalid API keys', 'message': 'Keys invalid'}), 403

        return f(*args, **kwargs)
    return decorated_function

# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy',
        'service': 'Netzone API',
        'version': '1.0.0'
    }), 200

@app.route('/api/v2rays')
@require_api_keys
def api_v2rays():
    try:
        data = load_json('free_v2rays.json')
        return jsonify({'success': True, 'count': len(data.get('vpn_configs', [])), 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps')
def api_apps():
    try:
        data = load_json('apps.json')
        return jsonify({'success': True, 'count': len(data.get('apps', [])), 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/whatsapp')
def whatsapp():
    return redirect("https://chat.whatsapp.com/Hre9DcY71UvC32oMVwwUrE", code=302)

@app.route('/discord')
def discord():
    return redirect("https://discord.gg/DhPZ8uMv4v", code=302)

# =========================
# ERROR HANDLING
# =========================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('404.html'), 500

# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
