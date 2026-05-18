from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# TELEGRAM BOT PERMANENT STORAGE
# ============================================
BOT_TOKEN = "8981073322:AAHmyVlyLjlab1_hOZBllWSKHsJPWMM7smE"
CHAT_ID = "8721224557"

def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=5)
    except:
        pass

def tg_get():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url, timeout=5)
        return resp.json()
    except:
        return {"ok": False}

# ============================================
# UNIVERSAL STORAGE API
# ============================================

@app.route('/<name>', methods=['POST'])
def save(name):
    """SAVE: Jo bhi JSON bhejo - Permanent save hoga"""
    try:
        data = request.get_json(force=True, silent=True)
        
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Format for Telegram
        text = f"📦{name}|{datetime.now().strftime('%H:%M:%S')}|{json.dumps(data, ensure_ascii=False)}"
        tg_send(text)
        
        return jsonify({
            "status": "✅ SAVED",
            "name": name,
            "storage": "Telegram Cloud - PERMANENT"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<name>', methods=['GET'])
def get(name):
    """GET: Latest saved data return karo"""
    try:
        updates = tg_get()
        
        if updates.get('ok'):
            # Reverse search - latest first
            for msg in reversed(updates['result']):
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if text.startswith(f'📦{name}|'):
                        try:
                            # Extract JSON part
                            parts = text.split('|', 2)
                            if len(parts) >= 3:
                                return jsonify(json.loads(parts[2]))
                        except:
                            pass
        
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<name>', methods=['DELETE'])
def delete(name):
    """DELETE: Mark as deleted"""
    tg_send(f"❌DELETED|{name}|{datetime.now().strftime('%H:%M:%S')}")
    return jsonify({"status": "✅ DELETED", "name": name})

@app.route('/<name>/all', methods=['GET'])
def get_all(name):
    """GET ALL: Sab versions of data"""
    try:
        updates = tg_get()
        results = []
        
        if updates.get('ok'):
            for msg in updates['result']:
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if text.startswith(f'📦{name}|'):
                        try:
                            parts = text.split('|', 2)
                            if len(parts) >= 3:
                                results.append({
                                    "time": parts[1],
                                    "data": json.loads(parts[2])
                                })
                        except:
                            pass
        
        return jsonify({"name": name, "count": len(results), "history": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list', methods=['GET'])
def list_all():
    """LIST: Sab saved names"""
    try:
        updates = tg_get()
        names = set()
        
        if updates.get('ok'):
            for msg in updates['result']:
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if text.startswith('📦') and '|' in text:
                        name = text[1:].split('|')[0]
                        names.add(name)
        
        return jsonify({"names": list(names), "count": len(names)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "service": "🗄️ BRONX UNIVERSAL STORAGE API",
        "storage": "Telegram Cloud - 100% PERMANENT",
        "version": "2.0",
        "endpoints": {
            "save": "POST /{name}",
            "get": "GET /{name}",
            "delete": "DELETE /{name}",
            "history": "GET /{name}/all",
            "list": "GET /list"
        },
        "usage_examples": {
            "curl_save": 'curl -X POST https://bromx-db-stroge.onrender.com/keys -H "Content-Type: application/json" -d \'{"myKey":"myValue"}\'',
            "curl_get": "curl https://bromx-db-stroge.onrender.com/keys",
            "js_save": "fetch('/keys', {method:'POST', body:JSON.stringify({data:'here'})})",
            "js_get": "fetch('/keys').then(r=>r.json())"
        },
        "credit": "@BRONX_ULTRA"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
