from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ============================================
# BOT CONFIG
# ============================================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8981073322:AAHmyVlyLjlab1_hOZBllWSKHsJPWMM7smE')
CHAT_ID = os.environ.get('CHAT_ID', '8721224557')

def send_tg(text):
    """Telegram pe message bhejo"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]})
    return resp.json()

def get_tg_messages():
    """Telegram se sab messages lo"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    resp = requests.get(url)
    return resp.json()

# ============================================
# STORAGE API - KISI BHI PROJECT SE CALL KARO
# ============================================

@app.route('/store', methods=['POST'])
def store():
    """Koi bhi data store karo"""
    data = request.get_json()
    
    # Format for Telegram
    text = f"📦 BRONX_STORE\n🆔 {data.get('id', 'auto')}\n📝 {json.dumps(data, ensure_ascii=False)[:3500]}"
    
    result = send_tg(text)
    
    if result.get('ok'):
        return jsonify({
            "status": "✅ Stored",
            "message_id": result['result']['message_id'],
            "storage": "Telegram Cloud - PERMANENT"
        })
    
    return jsonify({"status": "❌", "error": result}), 500

@app.route('/store/keys', methods=['POST'])
def store_keys():
    """API Keys store karo"""
    data = request.get_json()
    
    text = f"""🔑 KEY_STORE
━━━━━━━━━━━━━━━
Key: {data.get('key','')}
Owner: {data.get('owner','')}
Limit: {data.get('limit','')}
Scopes: {data.get('scopes',[])}
Expiry: {data.get('expiry','')}
Time: {datetime.now().isoformat()}
━━━━━━━━━━━━━━━"""
    
    send_tg(text)
    return jsonify({"status": "✅ Key Stored Permanently"})

@app.route('/store/log', methods=['POST'])
def store_log():
    """Activity logs store karo"""
    data = request.get_json()
    text = f"📋 LOG | {data.get('action','')} | {data.get('user','')} | {datetime.now().isoformat()}"
    send_tg(text)
    return jsonify({"status": "✅ Logged"})

@app.route('/get', methods=['GET'])
def get_data():
    """Stored data retrieve karo"""
    updates = get_tg_messages()
    
    if updates.get('ok'):
        messages = []
        for msg in updates['result']:
            if 'message' in msg and 'text' in msg['message']:
                if 'BRONX_STORE' in msg['message']['text']:
                    messages.append({
                        "id": msg['message']['message_id'],
                        "text": msg['message']['text'],
                        "date": msg['message']['date']
                    })
        
        return jsonify({
            "status": "✅",
            "total": len(messages),
            "data": messages[-50:]  # Last 50 records
        })
    
    return jsonify({"status": "❌", "error": "Cannot fetch"}), 500

@app.route('/setup', methods=['GET'])
def setup():
    """Auto-detect Chat ID"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    resp = requests.get(url)
    data = resp.json()
    
    if data.get('ok') and data['result']:
        chat_id = data['result'][-1]['message']['chat']['id']
        return jsonify({
            "status": "✅",
            "chat_id": chat_id,
            "set_env": f"CHAT_ID={chat_id}"
        })
    
    return jsonify({
        "status": "❌",
        "help": "Bot ko /start bhejo pehle!"
    })

@app.route('/')
def home():
    return jsonify({
        "service": "🗄️ BRONX EXTERNAL STORAGE API",
        "storage": "Telegram Cloud (Permanent & Free)",
        "endpoints": {
            "store_data": "POST /store",
            "store_keys": "POST /store/keys",
            "store_logs": "POST /store/log",
            "get_data": "GET /get",
            "auto_setup": "GET /setup"
        },
        "how_to_use": {
            "from_python": "requests.post('URL/store', json={'key':'value'})",
            "from_js": "fetch('URL/store', {method:'POST', body:JSON.stringify({key:'value'})})"
        },
        "credit": "@BRONX_ULTRA"
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
