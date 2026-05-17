from flask import Flask, request, jsonify, render_template_string
from supabase import create_client
from datetime import datetime

app = Flask(__name__)

# ============================================
# SUPABASE CONFIG
# ============================================
SUPABASE_URL = "https://kzedjjswtuveudssyzaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt6ZWRqanN3dHV2ZXVkc3N5emFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjM2NTQsImV4cCI6MjA5NDU5OTY1NH0.7iqsEcY6n-hy81CvYqDFnvuIRoLwEZ7oiC6rgfHbzQ0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================
# SIMPLE HTML UI
# ============================================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BRONX PERMANENT STORAGE</title>
    <style>
        body{background:#000;color:#0f0;font-family:monospace;padding:20px}
        .box{background:#111;border:1px solid #0f0;padding:20px;margin:10px 0;border-radius:10px}
        input,textarea,select{width:100%;padding:10px;background:#000;border:1px solid #0f0;color:#0f0;margin:5px 0;border-radius:5px}
        button{background:#0f0;color:#000;padding:12px 30px;border:none;border-radius:5px;font-weight:bold;cursor:pointer}
        pre{background:#000;padding:10px;border-radius:5px;color:#0f0;max-height:300px;overflow:auto}
        .card{background:#0a0a0a;border:1px solid #333;padding:15px;margin:5px 0;border-radius:5px}
    </style>
</head>
<body>
    <h1>🗄️ BRONX PERMANENT STORAGE</h1>
    <p style="color:#888">Data Save Karo - Kabhi Delete Nahi Hoga!</p>
    
    <div class="box">
        <h3>📦 SAVE DATA</h3>
        <input type="text" id="keyName" placeholder="Data Name (e.g., my_key)">
        <textarea id="jsonData" rows="4" placeholder='{"name":"BRONX","plan":"premium"}'></textarea>
        <button onclick="saveData()">💾 SAVE PERMANENTLY</button>
    </div>
    
    <div class="box">
        <h3>📋 GET ALL DATA</h3>
        <button onclick="loadData()">🔍 LOAD DATA</button>
        <pre id="result"></pre>
    </div>
    
    <div class="box">
        <h3>🔍 SEARCH DATA</h3>
        <input type="text" id="searchKey" placeholder="Search by name...">
        <button onclick="searchData()">🔎 SEARCH</button>
        <div id="searchResult"></div>
    </div>
    
    <script>
        async function saveData(){
            const name = document.getElementById('keyName').value;
            const data = document.getElementById('jsonData').value;
            
            if(!name || !data){
                alert('Please fill all fields!');
                return;
            }
            
            try{
                const jsonData = JSON.parse(data);
                const resp = await fetch('/save', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({name:name, data:jsonData})
                });
                const result = await resp.json();
                alert('✅ SAVED PERMANENTLY!');
                loadData();
            }catch(e){
                alert('❌ Error: ' + e.message);
            }
        }
        
        async function loadData(){
            const resp = await fetch('/get');
            const result = await resp.json();
            document.getElementById('result').textContent = JSON.stringify(result, null, 2);
        }
        
        async function searchData(){
            const key = document.getElementById('searchKey').value;
            const resp = await fetch('/get?search=' + key);
            const result = await resp.json();
            
            let html = '';
            if(result.data){
                result.data.forEach(item => {
                    html += `<div class="card">
                        <b>${item.name}</b><br>
                        <pre>${JSON.stringify(item.data, null, 2)}</pre>
                        <small>${item.created_at}</small>
                    </div>`;
                });
            }
            document.getElementById('searchResult').innerHTML = html || 'No data found';
        }
        
        loadData();
    </script>
</body>
</html>
"""

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def home():
    return HTML

@app.route('/save', methods=['POST'])
def save():
    """Data PERMANENTLY save karo"""
    try:
        body = request.get_json()
        name = body.get('name', 'unnamed')
        data = body.get('data', {})
        
        record = {
            "name": name,
            "data": data,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table('storage').insert(record).execute()
        
        return jsonify({
            "status": "✅ PERMANENTLY SAVED!",
            "message": "Data kabhi delete nahi hoga!",
            "record": result.data
        })
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 500

@app.route('/get')
def get_data():
    """Sab data lo"""
    try:
        search = request.args.get('search', '')
        
        if search:
            result = supabase.table('storage').select("*").ilike('name', f'%{search}%').execute()
        else:
            result = supabase.table('storage').select("*").order('created_at', desc=True).limit(50).execute()
        
        return jsonify({
            "status": "✅",
            "count": len(result.data),
            "data": result.data
        })
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 500

@app.route('/delete', methods=['POST'])
def delete():
    """Data delete karo"""
    try:
        body = request.get_json()
        name = body.get('name', '')
        
        result = supabase.table('storage').delete().eq('name', name).execute()
        
        return jsonify({
            "status": "✅ Deleted",
            "deleted": result.data
        })
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 500

# ============================================
# QUICK STORE (KISI BHI PROJECT SE CALL KARO)
# ============================================
@app.route('/store', methods=['POST'])
def quick_store():
    """Quick store - Sirf data bhejo"""
    try:
        data = request.get_json() or {}
        
        record = {
            "name": data.get('name', 'auto_' + datetime.now().strftime('%Y%m%d%H%M%S')),
            "data": data,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table('storage').insert(record).execute()
        
        return jsonify({"status": "✅ Stored", "id": result.data[0]['name'] if result.data else 'unknown'})
    except Exception as e:
        return jsonify({"status": "❌", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
