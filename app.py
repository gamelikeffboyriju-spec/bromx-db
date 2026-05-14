from flask import Flask, request, jsonify, render_template_string
import json
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# ============================================
# STORAGE FILE (Render Persistent)
# ============================================
STORAGE_FILE = "/opt/render/project/src/data_storage.json"
ADMIN_PASSWORD = "bronx2026"

# ============================================
# LOAD / SAVE FUNCTIONS
# ============================================
def load_data():
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"keys": {}, "settings": {}, "logs": []}

def save_data(data):
    try:
        os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

# ============================================
# ADMIN PANEL HTML
# ============================================
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BRONX ADMIN</title>
    <meta charset="UTF-8">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#000;color:#bf00ff;font-family:monospace;padding:20px}
        .header{text-align:center;padding:30px;border:2px solid #bf00ff;border-radius:15px;margin-bottom:20px}
        h1{color:#bf00ff;text-shadow:0 0 20px #bf00ff}
        .panel{background:#111;border:1px solid #bf00ff;border-radius:10px;padding:20px;margin:15px 0}
        input,select{width:100%;padding:12px;background:#000;border:1px solid #bf00ff;border-radius:8px;color:#bf00ff;margin:8px 0;font-family:monospace}
        .btn{padding:12px 25px;background:#bf00ff;color:#000;border:none;border-radius:8px;cursor:pointer;font-weight:bold;margin:5px}
        .btn:hover{box-shadow:0 0 20px #bf00ff}
        table{width:100%;border-collapse:collapse;margin-top:15px}
        th{background:#bf00ff;color:#000;padding:10px}
        td{padding:8px;border-bottom:1px solid #333;color:#fff}
        .badge{padding:4px 10px;border-radius:20px;font-size:11px}
        .active{background:#0f02;color:#0f0}
        .expired{background:#f002;color:#f00}
        .toast{position:fixed;bottom:20px;right:20px;background:#bf00ff;color:#000;padding:15px 25px;border-radius:10px;font-weight:bold;z-index:999}
        .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:20px}
        .stat{background:#111;border:1px solid #bf00ff;padding:15px;text-align:center;border-radius:10px}
        .stat-val{font-size:28px;color:#bf00ff;font-weight:bold}
        .stat-label{color:#888;font-size:12px}
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 BRONX ULTRA KEY MANAGER</h1>
        <p style="color:#888;">Data Storage API | Admin Panel</p>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-val" id="totalKeys">0</div><div class="stat-label">TOTAL KEYS</div></div>
        <div class="stat"><div class="stat-val" id="activeKeys">0</div><div class="stat-label">ACTIVE KEYS</div></div>
        <div class="stat"><div class="stat-val" id="totalUsed">0</div><div class="stat-label">TOTAL USED</div></div>
        <div class="stat"><div class="stat-val" id="apisCount">0</div><div class="stat-label">SCOPES</div></div>
    </div>
    
    <div class="panel">
        <h2 style="color:#bf00ff;">🔑 GENERATE NEW KEY</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px">
            <div>
                <label style="color:#888;">OWNER NAME</label>
                <input type="text" id="ownerName" value="Premium User">
            </div>
            <div>
                <label style="color:#888;">REQUEST LIMIT</label>
                <input type="number" id="limit" value="100">
            </div>
            <div>
                <label style="color:#888;">EXPIRY (Days)</label>
                <input type="number" id="expiryDays" value="30">
            </div>
            <div>
                <label style="color:#888;">SCOPES</label>
                <select id="scopes" multiple style="height:80px">
                    <option value="number">Number Lookup</option>
                    <option value="aadhar">Aadhar Lookup</option>
                    <option value="vehicle">Vehicle Info</option>
                    <option value="tg">Telegram Info</option>
                    <option value="all">ALL SCOPES</option>
                </select>
            </div>
        </div>
        <button class="btn" onclick="generateKey()" style="width:100%;margin-top:15px">🚀 GENERATE API KEY</button>
    </div>
    
    <div class="panel">
        <h2 style="color:#bf00ff;">📋 ALL KEYS</h2>
        <div style="max-height:400px;overflow-y:auto">
            <table>
                <thead>
                    <tr><th>KEY</th><th>OWNER</th><th>LIMIT</th><th>USED</th><th>EXPIRY</th><th>SCOPES</th><th>STATUS</th><th>ACTION</th></tr>
                </thead>
                <tbody id="keysTable"></tbody>
            </table>
        </div>
    </div>
    
    <div id="toast" class="toast" style="display:none"></div>
    
    <script>
        const SCOPES_LIST = ['number','aadhar','vehicle','tg','pan','upi','ifsc','pincode','ip','all'];
        
        async function loadData(){
            const res = await fetch('/admin/keys');
            const data = await res.json();
            
            if(data.success){
                const keys = data.keys;
                const arr = Object.entries(keys);
                
                document.getElementById('totalKeys').textContent = arr.length;
                document.getElementById('activeKeys').textContent = arr.filter(([k,v])=>v.status==='active').length;
                document.getElementById('totalUsed').textContent = arr.reduce((s,[k,v])=>s+(v.used||0),0);
                document.getElementById('apisCount').textContent = SCOPES_LIST.length;
                
                document.getElementById('keysTable').innerHTML = arr.map(([key,val])=>{
                    const status = val.status === 'active' ? '<span class="badge active">ACTIVE</span>' : '<span class="badge expired">EXPIRED</span>';
                    return `<tr>
                        <td><code style="color:#bf00ff;">${key.substring(0,15)}...</code></td>
                        <td>${val.owner}</td>
                        <td>${val.limit}</td>
                        <td>${val.used||0}</td>
                        <td>${val.expiry||'Never'}</td>
                        <td>${(val.scopes||[]).join(', ')}</td>
                        <td>${status}</td>
                        <td>
                            <button onclick="deleteKey('${key}')" style="background:red;color:#fff;border:none;padding:4px 8px;border-radius:5px;cursor:pointer">🗑️</button>
                        </td>
                    </tr>`;
                }).join('');
            }
        }
        
        async function generateKey(){
            const name = document.getElementById('ownerName').value || 'User';
            const limit = document.getElementById('limit').value || 100;
            const expiry = document.getElementById('expiryDays').value || 30;
            const scopes = Array.from(document.getElementById('scopes').selectedOptions).map(o=>o.value);
            
            const res = await fetch('/admin/generate', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({owner:name, limit:parseInt(limit), expiryDays:parseInt(expiry), scopes})
            });
            
            const data = await res.json();
            if(data.success){
                showToast('✅ Key Generated: ' + data.key);
                loadData();
            } else {
                showToast('❌ Error: ' + data.error);
            }
        }
        
        async function deleteKey(key){
            if(!confirm('Delete this key?')) return;
            await fetch('/admin/delete', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({key})
            });
            showToast('✅ Key Deleted!');
            loadData();
        }
        
        function showToast(msg){
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.style.display = 'block';
            setTimeout(()=>t.style.display='none', 3000);
        }
        
        loadData();
    </script>
</body>
</html>
"""

# ============================================
# API ROUTES
# ============================================

# Public: Verify & Use Key
@app.route('/api/verify', methods=['GET'])
def verify_key():
    api_key = request.args.get('key', '')
    data = load_data()
    
    if api_key not in data['keys']:
        return jsonify({"valid": False, "error": "Invalid key"}), 403
    
    key_data = data['keys'][api_key]
    
    # Check expiry
    if key_data.get('expiry'):
        exp = datetime.fromisoformat(key_data['expiry'])
        if datetime.now() > exp:
            return jsonify({"valid": False, "error": "Key expired"}), 403
    
    # Check limit
    if key_data['used'] >= key_data['limit']:
        return jsonify({"valid": False, "error": "Limit exhausted"}), 403
    
    # Increment usage
    key_data['used'] = key_data.get('used', 0) + 1
    save_data(data)
    
    return jsonify({
        "valid": True,
        "owner": key_data['owner'],
        "remaining": key_data['limit'] - key_data['used'],
        "scopes": key_data.get('scopes', [])
    })

# ============================================
# ADMIN ROUTES
# ============================================
@app.route('/admin')
def admin_panel():
    return ADMIN_HTML

@app.route('/admin/keys')
def admin_keys():
    data = load_data()
    return jsonify({"success": True, "keys": data['keys']})

@app.route('/admin/generate', methods=['POST'])
def admin_generate():
    try:
        body = request.get_json()
        owner = body.get('owner', 'User')
        limit = body.get('limit', 100)
        expiry_days = body.get('expiryDays', 30)
        scopes = body.get('scopes', ['all'])
        
        # Generate unique key
        new_key = "BRONX_" + uuid.uuid4().hex[:12].upper()
        
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        data = load_data()
        data['keys'][new_key] = {
            "owner": owner,
            "limit": limit,
            "used": 0,
            "scopes": scopes,
            "expiry": expiry_date,
            "status": "active",
            "created": datetime.now().isoformat()
        }
        
        save_data(data)
        
        return jsonify({
            "success": True,
            "key": new_key,
            "message": "Key generated successfully!"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    try:
        body = request.get_json()
        key = body.get('key', '')
        
        data = load_data()
        if key in data['keys']:
            del data['keys'][key]
            save_data(data)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Key not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
