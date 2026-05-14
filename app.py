from flask import Flask, request, jsonify
import json
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# ============================================
# RENDER DISK PATH (PERSISTENT - Kabhi delete nahi hoga)
# ============================================
DATA_DIR = "/opt/render/project/src/data"
DATA_FILE = os.path.join(DATA_DIR, "database.json")

# Auto-create directory
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================
def load_db():
    """Load database from file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_db(data):
    """Save database to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Save Error: {e}")
        return False

# ============================================
# PUBLIC API - Store Any Data
# ============================================
@app.route('/store', methods=['POST'])
def store_data():
    """Koi bhi JSON data store karo"""
    try:
        data = request.get_json()
        
        # Generate unique ID
        record_id = data.get('id') or str(uuid.uuid4())[:8]
        
        db = load_db()
        db[record_id] = {
            "data": data,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        save_db(db)
        
        return jsonify({
            "status": "✅ Stored",
            "id": record_id,
            "total_records": len(db)
        })
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 400

@app.route('/get/<record_id>', methods=['GET'])
def get_data(record_id):
    """Stored data retrieve karo"""
    db = load_db()
    
    if record_id in db:
        return jsonify({
            "status": "✅ Found",
            "data": db[record_id]
        })
    
    return jsonify({"status": "❌ Not Found"}), 404

@app.route('/get/all', methods=['GET'])
def get_all():
    """Sab data ek saath"""
    db = load_db()
    return jsonify({
        "status": "✅",
        "total": len(db),
        "records": db
    })

@app.route('/update/<record_id>', methods=['PUT'])
def update_data(record_id):
    """Existing data update karo"""
    try:
        new_data = request.get_json()
        db = load_db()
        
        if record_id in db:
            db[record_id]['data'].update(new_data)
            db[record_id]['updated'] = datetime.now().isoformat()
            save_db(db)
            return jsonify({"status": "✅ Updated"})
        
        return jsonify({"status": "❌ Not Found"}), 404
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 400

@app.route('/delete/<record_id>', methods=['DELETE'])
def delete_data(record_id):
    """Record delete karo"""
    db = load_db()
    
    if record_id in db:
        del db[record_id]
        save_db(db)
        return jsonify({"status": "✅ Deleted", "remaining": len(db)})
    
    return jsonify({"status": "❌ Not Found"}), 404

# ============================================
# KEY MANAGEMENT SPECIFIC API
# ============================================
@app.route('/keys/generate', methods=['POST'])
def generate_key():
    """API Key generate karo"""
    try:
        body = request.get_json() or {}
        
        new_key = "BRONX_" + uuid.uuid4().hex[:16].upper()
        
        key_data = {
            "key": new_key,
            "owner": body.get('owner', 'User'),
            "limit": body.get('limit', 100),
            "used": 0,
            "scopes": body.get('scopes', ['all']),
            "status": "active",
            "expiry": (datetime.now() + timedelta(days=body.get('days', 30))).isoformat(),
            "created": datetime.now().isoformat()
        }
        
        db = load_db()
        
        # Keys section me store
        if 'api_keys' not in db:
            db['api_keys'] = {}
        
        db['api_keys'][new_key] = key_data
        save_db(db)
        
        return jsonify({
            "status": "✅ Key Generated",
            "key": new_key,
            "details": key_data
        })
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 400

@app.route('/keys/verify', methods=['GET'])
def verify_key():
    """Key verify karo"""
    api_key = request.args.get('key', '')
    
    db = load_db()
    keys = db.get('api_keys', {})
    
    if api_key not in keys:
        return jsonify({"valid": False, "error": "Invalid key"}), 403
    
    key_data = keys[api_key]
    
    # Check expiry
    if key_data.get('expiry'):
        if datetime.now() > datetime.fromisoformat(key_data['expiry']):
            return jsonify({"valid": False, "error": "Expired"}), 403
    
    # Check limit
    if key_data['used'] >= key_data['limit']:
        return jsonify({"valid": False, "error": "Limit exhausted"}), 403
    
    # Increment
    key_data['used'] += 1
    save_db(db)
    
    return jsonify({
        "valid": True,
        "owner": key_data['owner'],
        "remaining": key_data['limit'] - key_data['used']
    })

@app.route('/keys/all', methods=['GET'])
def all_keys():
    """Sab keys list"""
    db = load_db()
    return jsonify({
        "status": "✅",
        "total_keys": len(db.get('api_keys', {})),
        "keys": db.get('api_keys', {})
    })

# ============================================
# DATABASE STATS
# ============================================
@app.route('/stats', methods=['GET'])
def db_stats():
    db = load_db()
    
    # File size
    file_size = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
    
    return jsonify({
        "status": "✅",
        "file_path": DATA_FILE,
        "file_size_kb": round(file_size / 1024, 2),
        "total_records": len(db),
        "sections": list(db.keys()),
        "credit": "@BRONX_ULTRA"
    })

@app.route('/')
def home():
    return jsonify({
        "service": "BRONX ULTRA DATA STORAGE API",
        "endpoints": {
            "store": "POST /store",
            "get": "GET /get/<id>",
            "get_all": "GET /get/all",
            "update": "PUT /update/<id>",
            "delete": "DELETE /delete/<id>",
            "generate_key": "POST /keys/generate",
            "verify_key": "GET /keys/verify?key=KEY",
            "stats": "GET /stats"
        },
        "credit": "@BRONX_ULTRA"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
