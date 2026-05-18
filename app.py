from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ============================================
# TELEGRAM BOT STORAGE (PERMANENT)
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
# ADMIN PANEL HTML
# ============================================
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BRONX ADMIN</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a0a;color:#bf00ff;font-family:monospace;padding:15px}
        .header{text-align:center;padding:20px;border:2px solid #bf00ff;border-radius:10px;margin-bottom:15px;background:#111}
        h1{font-size:22px;text-shadow:0 0 20px #bf00ff}
        .card{background:#111;border:1px solid #bf00ff;border-radius:10px;padding:15px;margin:10px 0}
        .card h3{color:#bf00ff;margin-bottom:10px;font-size:16px}
        input,select{width:100%;padding:10px;background:#000;border:1px solid #bf00ff;border-radius:6px;color:#bf00ff;margin:6px 0;font-family:monospace;font-size:13px}
        label{color:#888;font-size:11px;display:block;margin-top:5px}
        .btn{width:100%;padding:12px;background:#bf00ff;color:#000;border:none;border-radius:6px;font-weight:bold;cursor:pointer;font-size:14px;margin:8px 0}
        .btn:hover{box-shadow:0 0 20px #bf00ff}
        .btn-red{background:#ff3333;color:#fff}
        .btn-green{background:#00cc44;color:#000}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
        .key-card{background:#0a0a0a;border:1px solid #333;padding:10px;margin:6px 0;border-radius:6px;font-size:11px}
        .key-card .k{color:#ff0;font-size:10px}
        .key-card .v{color:#0ff}
        .badge{padding:3px 8px;border-radius:10px;font-size:9px;font-weight:bold}
        .active{background:#0f02;color:#0f0}
        .expired{background:#f002;color:#f00}
        .toast{position:fixed;bottom:15px;right:15px;background:#bf00ff;color:#000;padding:12px 20px;border-radius:8px;font-weight:bold;z-index:999;display:none;font-size:13px}
        .result-box{background:#000;padding:10px;border-radius:6px;margin-top:10px;display:none;max-height:200px;overflow:auto;font-size:11px}
        code{color:#0f0;word-break:break-all}
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 BRONX ADMIN PANEL</h1>
        <p style="color:#888;font-size:11px">Telegram Permanent Storage | Key Manager</p>
    </div>
    
    <!-- Key Generator -->
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
        <label>SCOPES</label>
        <select id="scopes" multiple style="height:80px">
            <option value="all" selected>ALL</option>
            <option value="number">Number</option>
            <option value="aadhar">Aadhar</option>
            <option value="vehicle">Vehicle</option>
            <option value="tg">Telegram</option>
        </select>
        <button class="btn" onclick="generateKey()">🚀 GENERATE KEY</button>
        <div id="genResult" class="result-box"></div>
    </div>
    
    <!-- View Keys -->
    <div class="card">
        <h3>📋 ALL KEYS</h3>
        <button class="btn btn-green" onclick="loadKeys()">🔄 REFRESH KEYS</button>
        <div id="keysList" style="margin-top:10px;max-height:300px;overflow:auto"></div>
    </div>
    
    <!-- Quick Test -->
    <div class="card">
        <h3>🧪 TEST STORAGE</h3>
        <div class="row">
            <div><label>PROJECT NAME</label><input type="text" id="projName" value="test"></div>
            <div><label>JSON DATA</label><input type="text" id="projData" value='{"test":"hello"}'></div>
        </div>
        <button class="btn" onclick="testSave()">💾 SAVE</button>
        <button class="btn btn-green" onclick="testGet()">📖 GET</button>
        <div id="testResult" class="result-box"></div>
    </div>
    
    <div id="toast" class="toast"></div>
    
    <script>
        function toast(msg){let t=document.getElementById('toast');t.textContent=msg;t.style.display='block';setTimeout(()=>t.style.display='none',2000)}
        function show(id,data){let d=document.getElementById(id);d.textContent=JSON.stringify(data,null,2);d.style.display='block'}
        
        async function generateKey(){
            let key=document.getElementById('keyName').value||'BRONX_'+Date.now().toString(36).toUpperCase()
            let owner=document.getElementById('owner').value||'User'
            let limit=parseInt(document.getElementById('limit').value)||100
            let expiry=parseInt(document.getElementById('expiry').value)||30
            let scopes=Array.from(document.getElementById('scopes').selectedOptions).map(o=>o.value)
            
            let payload={key,owner,limit,expiry,scopes}
            
            try{
                let r=await fetch('/admin/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
                let d=await r.json()
                if(d.success){toast('✅ KEY GENERATED!');show('genResult',d);loadKeys()}
                else toast('❌ '+d.error)
            }catch(e){toast('❌ Error')}
        }
        
        async function loadKeys(){
            try{
                let r=await fetch('/admin/keys')
                let d=await r.json()
                let html=''
                if(d.keys) Object.entries(d.keys).forEach(([k,v])=>{
                    let status=v.status==='active'?'active':'expired'
                    html+=`<div class="key-card">
                        <span class="k">🔑 ${k}</span><br>
                        <span class="v">👤 ${v.owner} | 📊 ${v.limit} | ✅ ${v.used||0} | ⏰ ${v.expiry||'Never'} | </span><span class="badge ${status}">${v.status}</span>
                    </div>`
                })
                document.getElementById('keysList').innerHTML=html||'<p style="color:#888">No keys</p>'
            }catch(e){}
        }
        
        async function testSave(){
            let proj=document.getElementById('projName').value
            let data=document.getElementById('projData').value
            try{
                let json=JSON.parse(data)
                let r=await fetch('/'+proj,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(json)})
                let d=await r.json()
                show('testResult',d)
                toast('✅ SAVED!')
            }catch(e){toast('❌ Invalid JSON')}
        }
        
        async function testGet(){
            let proj=document.getElementById('projName').value
            try{
                let r=await fetch('/'+proj)
                let d=await r.json()
                show('testResult',d)
            }catch(e){toast('❌ Error')}
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
        
        return jsonify({"status": "✅ SAVED PERMANENTLY", "project": project})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# ADMIN ROUTES
# ============================================
@app.route('/admin/generate', methods=['POST'])
def admin_generate():
    try:
        body = request.get_json()
        key = body.get('key', '')
        owner = body.get('owner', 'User')
        limit = body.get('limit', 100)
        expiry_days = body.get('expiry', 30)
        scopes = body.get('scopes', ['all'])
        
        if not key:
            return jsonify({"success": False, "error": "Key name required"}), 400
        
        expiry = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d") if expiry_days > 0 else "Never"
        
        key_data = {
            "owner": owner,
            "limit": limit,
            "used": 0,
            "scopes": scopes,
            "expiry": expiry,
            "status": "active",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save to Telegram
        text = f"🔑 KEY_STORE\nKEY:{key}\n{json.dumps(key_data, indent=2)}"
        tg_send(text)
        
        return jsonify({"success": True, "key": key, "data": key_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/keys')
def admin_keys():
    try:
        updates = tg_get()
        keys = {}
        
        if updates.get('ok'):
            for msg in updates['result']:
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if '🔑 KEY_STORE' in text:
                        try:
                            key_match = text.split('KEY:')[1].split('\n')[0].strip()
                            json_start = text.index('{')
                            key_data = json.loads(text[json_start:])
                            keys[key_match] = key_data
                        except:
                            pass
        
        return jsonify({"success": True, "keys": keys})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/')
def home():
    return ADMIN_HTML

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
