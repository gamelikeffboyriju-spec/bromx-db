from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# TERA BOT CREDENTIALS (ALREADY WORKING ✅)
# ============================================
BOT_TOKEN = "8981073322:AAHmyVlyLjlab1_hOZBllWSKHsJPWMM7smE"
CHAT_ID = "8721224557"

def send_to_telegram(text):
    """Telegram pe message bhejo"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text[:4096],
        "parse_mode": "HTML"
    }, timeout=10)
    return resp.json()

def get_from_telegram():
    """Telegram se messages lo"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    resp = requests.get(url, timeout=10)
    return resp.json()

# ============================================
# UNIVERSAL DATABASE ROUTES
# ============================================

@app.route('/<project>', methods=['GET'])
def get_data(project):
    """GET: Telegram se data retrieve karo"""
    try:
        updates = get_from_telegram()
        
        if not updates.get('ok'):
            return jsonify({"error": "Cannot fetch"}), 500
        
        # Find latest data for this project
        for msg in reversed(updates['result']):
            if 'message' in msg and 'text' in msg['message']:
                text = msg['message']['text']
                if f'📦 PROJECT:{project}' in text:
                    # Extract JSON data
                    try:
                        start = text.index('DATA:') + 5
                        data_text = text[start:].strip()
                        data = json.loads(data_text)
                        return jsonify(data)
                    except:
                        pass
        
        return jsonify({"status": "empty", "message": f"No data for '{project}'"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<project>', methods=['POST'])
def save_data(project):
    """POST: Telegram pe data save karo - KABHI DELETE NAHI HOGA"""
    try:
        body = request.get_json()
        
        if not body:
            return jsonify({"error": "No data"}), 400
        
        # Format message
        text = f"""📦 PROJECT:{project}
⏰ TIME:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
DATA:{json.dumps(body, indent=2, ensure_ascii=False)}"""
        
        result = send_to_telegram(text)
        
        if result.get('ok'):
            return jsonify({
                "status": "✅ SAVED PERMANENTLY",
                "project": project,
                "message_id": result['result']['message_id'],
                "storage": "Telegram Cloud - Kabhi delete nahi hoga!"
            })
        
        return jsonify({"error": "Send failed", "detail": result}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<project>', methods=['DELETE'])
def delete_data(project):
    """DELETE: Mark as deleted"""
    text = f"❌ DELETED:{project} | TIME:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_to_telegram(text)
    return jsonify({"status": "✅ DELETED", "project": project})

@app.route('/all')
def all_projects():
    """Sab projects list"""
    try:
        updates = get_from_telegram()
        projects = set()
        
        if updates.get('ok'):
            for msg in updates['result']:
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if '📦 PROJECT:' in text:
                        import re
                        match = re.search(r'PROJECT:(\w+)', text)
                        if match:
                            projects.add(match.group(1))
        
        return jsonify({"projects": list(projects), "count": len(projects)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "storage": "📱 TELEGRAM CLOUD - 100% PERMANENT",
        "guarantee": "Telegram servers - Messages never deleted!",
        "usage": {
            "save": "POST /{project}",
            "get": "GET /{project}",
            "delete": "DELETE /{project}",
            "list": "GET /all"
        },
        "example": "POST /keys → JSON data",
        "credit": "@BRONX_ULTRA"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
