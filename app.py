from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ============================================
# TELEGRAM BOT STORAGE
# ============================================
BOT_TOKEN = "8981073322:AAHmyVlyLjlab1_hOZBllWSKHsJPWMM7smE"
CHAT_ID = "8721224557"

def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=10)

def tg_get():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    resp = requests.get(url, timeout=10)
    return resp.json()

# ============================================
# ADMIN PANEL HTML (FIXED)
# ============================================
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BRONX ADMIN</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a0a;color:#bf00ff;font-family:monospace;padding:15px}
        .header{text-align:center;padding:20px;border:2px solid #bf00ff;border-radius:10px;margin-bottom:15px;background:#111}
        h1{font-size:22px;text-shadow:0 0 20px #bf00ff}
        .card{background:#111;border:1px solid #bf00ff;border-radius:10px;padding:15px;margin:10px 0}
        input,select{width:100%;padding:10px;background:#000;border:1px solid #bf00ff;border-radius:6px;color:#bf00ff;margin:6px 0;font-family:monospace}
        label{color:#888;font-size:11px;display:block;margin-top:5px}
        .btn{width:100%;padding:12px;background:#bf00ff;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;margin:8px 0}
        .btn-green{background:#00cc44;color:#000}
        .btn-red{background:#ff3333;color:#fff}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
        .key-card{background:#0a0a0a;border:1px solid #333;padding:8px;margin:5px 0;border-radius:5px;font-size:11px}
        .badge{padding:3px 8px;border-radius:10px;font-size:9px}
        .active{background:#0f02;color:#0f0}
        .toast{position:fixed;bottom:15px;right:15px;background:#bf00ff;color:#000;padding:12px 20px;border-radius:8px;font-weight:bold;z-index:999;display:none}
        pre{background:#000;padding:10px;border-radius:5px;color:#0f0;max-height:200px;overflow:auto;font-size:10px;margin-top:8px;display:none}
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 BRONX ADMIN PANEL</h1>
        <p style="color:#888;font-size:11px">Telegram Permanent Storage</p>
    </div>
    
    <div class="card">
        <h3>🔑 GENERATE API KEY</h3>
        <div class="row">
            <div><label>KEY NAME</label><input type="text" id="keyName" placeholder="BRONX_ABC"></div>
            <div><label>OWNER</label><input type="text" id="owner" value="Premium User"></div>
        </div>
        <div class="row">
            <div><label>LIMIT</label><input type="number" id="limit" value="100"></div>
            <div><label>EXPIRY (Days)</label><input type="number" id="expiry" value="30"></div>
        </div>
        <button class="btn" onclick="generateKey()">🚀 GENERATE KEY</button>
    </div>
    
    <div class="card">
        <h3>📋 ALL KEYS (<span id="keyCount">0</span>)</h3>
        <button class="btn btn-green" onclick="loadKeys()">🔄 REFRESH</button>
        <button class="btn btn-red" onclick="deleteAll()">🗑️ DELETE ALL</button>
        <div id="keysList" style="margin-top:10px;max-height:400px;overflow:auto"></div>
    </div>
    
    <div id="toast" class="toast"></div>
    
    <script>
        function toast(msg){let t=document.getElementById('toast');t.textContent=msg;t.style.display='block';setTimeout(()=>t.style.display='none',2000)}
        
        async function generateKey(){
            let key=document.getElementById('keyName').value
            if(!key){toast('❌ Enter key name!');return}
            let owner=document.getElementById('owner').value||'User'
            let limit=parseInt(document.getElementById('limit').value)||100
            let expiry=parseInt(document.getElementById('expiry').value)||30
            
            try{
                let r=await fetch('/admin/generate',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({key,owner,limit,expiry})
                })
                let d=await r.json()
                if(d.success){toast('✅ Key Generated!');loadKeys()}
                else toast('❌ '+d.error)
            }catch(e){toast('❌ Error')}
        }
        
        async function loadKeys(){
            try{
                let r=await fetch('/admin/keys')
                let d=await r.json()
                let html=''
                if(d.keys && Object.keys(d.keys).length>0){
                    document.getElementById('keyCount').textContent=Object.keys(d.keys).length
                    Object.entries(d.keys).forEach(([k,v])=>{
                        html+=`<div class="key-card">
                            <b style="color:#ff0">🔑 ${k}</b><br>
                            👤 ${v.owner} | 📊 ${v.limit||'∞'} | ✅ ${v.used||0} | ⏰ ${v.expiry||'Never'}
                            <span class="badge active">${v.status||'active'}</span>
                            <button onclick="deleteKey('${k}')" style="background:red;color:#fff;border:none;padding:2px 8px;border-radius:3px;margin-left:8px;cursor:pointer;font-size:10px">🗑️</button>
                        </div>`
                    })
                } else {
                    html='<p style="color:#888">No keys found. Generate one!</p>'
                }
                document.getElementById('keysList').innerHTML=html
            }catch(e){document.getElementById('keysList').innerHTML='<p style="color:red">Error loading keys</p>'}
        }
        
        async function deleteKey(key){
            if(!confirm('Delete '+key+'?'))return
            await fetch('/admin/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key})})
            toast('✅ Deleted!')
            loadKeys()
        }
        
        async function deleteAll(){
            if(!confirm('DELETE ALL KEYS?'))return
            await fetch('/admin/delete-all',{method:'POST'})
            toast('✅ All deleted!')
            loadKeys()
        }
        
        loadKeys()
    </script>
</body>
</html>
"""

# ============================================
# STORAGE ROUTES
# ============================================
@app.route('/<project>', methods=['GET'])
def get_data(project):
    try:
        updates = tg_get()
        if updates.get('ok'):
            for msg in reversed(updates['result']):
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if f'📦 PROJECT:{project}' in text:
                        try:
                            start = text.index('DATA:') + 5
                            return jsonify(json.loads(text[start:].strip()))
                        except:
                            pass
        return jsonify({"status": "empty"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<project>', methods=['POST'])
def save_data(project):
    try:
        body = request.get_json()
        if not body:
            return jsonify({"error": "No data"}), 400
        text = f"📦 PROJECT:{project}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nDATA:{json.dumps(body, ensure_ascii=False)}"
        tg_send(text)
        return jsonify({"status": "✅ SAVED", "project": project})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# ✅ FIXED ADMIN ROUTES
# ============================================
@app.route('/admin/generate', methods=['POST'])
def admin_generate():
    try:
        body = request.get_json()
        key = body.get('key', '')
        owner = body.get('owner', 'User')
        limit = int(body.get('limit', 100))
        expiry_days = int(body.get('expiry', 30))
        
        if not key:
            return jsonify({"success": False, "error": "Key name required"}), 400
        
        expiry = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d") if expiry_days > 0 else "Never"
        
        key_data = {"owner": owner, "limit": limit, "used": 0, "expiry": expiry, "status": "active"}
        
        # ✅ FIXED: Better format for parsing
        text = f"🔑KEY:{key}|{json.dumps(key_data)}"
        tg_send(text)
        
        return jsonify({"success": True, "key": key})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/keys')
def admin_keys():
    """✅ FIXED: Better parsing"""
    try:
        updates = tg_get()
        keys = {}
        
        if updates.get('ok'):
            for msg in updates['result']:
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    # ✅ Match new format
                    if '🔑KEY:' in text:
                        try:
                            # Extract key name and JSON
                            parts = text.split('|')
                            key_name = parts[0].replace('🔑KEY:', '').strip()
                            json_data = json.loads(parts[1])
                            keys[key_name] = json_data
                        except:
                            pass
                    # Also match old format
                    elif '🔑 KEY_STORE' in text:
                        try:
                            lines = text.split('\n')
                            key_name = lines[1].replace('KEY:', '').strip()
                            json_start = text.index('{')
                            json_data = json.loads(text[json_start:])
                            keys[key_name] = json_data
                        except:
                            pass
        
        return jsonify({"success": True, "keys": keys})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    body = request.get_json()
    key = body.get('key', '')
    tg_send(f"❌ DELETED:{key}")
    return jsonify({"success": True})

@app.route('/admin/delete-all', methods=['POST'])
def admin_delete_all():
    tg_send("❌ ALL KEYS DELETED")
    return jsonify({"success": True})

@app.route('/')
def home():
    return ADMIN_HTML

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
