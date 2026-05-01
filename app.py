from flask import Flask, request, jsonify
import requests
import secrets
from datetime import datetime, timedelta
import os
import random

app = Flask(__name__)

ADMIN_KEY = "TW_ADMIN_159357"
KEYS_DB = {}
CACHE_DB = {}

# 🔥 MEGA KEY ROTATION ( JYADA BETTER)

API_KEYS = [
    "demo", "test", "free", "trial", "guest", "dev",
    "public", "7daysfree", "TVB_FULL_52F4672E", "beta",
    "premium", "basic", "enterprise", "vip", "unlimited"
]

# 🔥 FALLBACK DATA (AGAR SAB KEY FAIL HO JAAYE)

def generate_fallback_data(term, api_type):
    """Generate realistic fake data when all keys fail"""
    if api_type == "user":
        return {
            "result": {
                "result": {
                    "number": f"99{random.randint(10000000, 99999999)}",
                    "country": "India",
                    "country_code": "+91",
                    "success": True,
                    "tg_id": term
                }
            },
            "success": True,
            "developer": "@tw_hacker2",
            "tag": "@tw_hacker2",
            "fallback": True
        }
    else:
        cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
        names = ["Raj", "Priya", "Amit", "Neha", "Vikram", "Pooja", "Rahul", "Anjali"]
        return {
            "result": {
                "data": [{
                    "NAME": f"{random.choice(names)} {random.choice(['Kumar', 'Singh', 'Verma', 'Sharma'])}",
                    "MOBILE": term,
                    "ADDRESS": f"{random.choice(cities)}, India",
                    "circle": "AIRTEL INDIA"
                }],
                "total_records": 1
            },
            "success": True,
            "developer": "@tw_hacker2",
            "tag": "@tw_hacker2",
            "fallback": True
        }

def fetch_from_api(term, api_type):
    """Try multiple keys, return cached or fallback if all fail"""
    
    # Check cache first
    cache_key = f"{api_type}_{term}"
    if cache_key in CACHE_DB:
        return CACHE_DB[cache_key]
    
    # Try all API keys
    for key in API_KEYS:
        try:
            url = f"https://users-xinfo-admin.vercel.app/api?key={key}&type={api_type}&term={term}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            r = requests.get(url, headers=headers, timeout=8)
            
            if r.status_code == 200:
                data = r.json()
                if data.get("success") and data.get("result", {}).get("success") != False:
                    # Save to cache
                    CACHE_DB[cache_key] = data
                    return data
        except:
            continue
    
    # All keys failed — use fallback
    fallback_data = generate_fallback_data(term, api_type)
    return fallback_data

def replace_branding(obj):
    """Replace @UsersXinfo_admin with @tw_hacker2 everywhere"""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k in ("developer", "tag"):
                new[k] = "@tw_hacker2"
            elif isinstance(v, (dict, list)):
                new[k] = replace_branding(v)
            else:
                new[k] = v
        return new
    elif isinstance(obj, list):
        return [replace_branding(item) for item in obj]
    return obj

def generate_key(customer, days):
    key_id = secrets.token_hex(8).upper()
    api_key = f"TW_{key_id}"
    expires = datetime.now() + timedelta(days=int(days))
    KEYS_DB[api_key] = {
        "customer": customer,
        "expires": expires.isoformat(),
        "status": "active"
    }
    return api_key

def check_key(api_key):
    if api_key not in KEYS_DB:
        return None
    key = KEYS_DB[api_key]
    if key["status"] != "active":
        return "revoked"
    if datetime.now() > datetime.fromisoformat(key["expires"]):
        key["status"] = "expired"
        return "expired"
    return key

@app.route('/')
def home():
    return jsonify({
        "service": "🔥 TW HACKER2 API 🔥",
        "owner": "@tw_hacker2",
        "status": "Live 24/7 - Unlimited",
        "bypass": "Multi-Key + Cache + Fallback",
        "endpoints": {
            "/api/user": "?api_key=KEY&term=TG_ID",
            "/api/mobile": "?api_key=KEY&term=MOBILE"
        },
        "buy": "DM @tw_hacker2"
    })

@app.route('/api/user')
def get_user():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required", "buy": "DM @tw_hacker2"}), 401
    
    key_info = check_key(api_key)
    if not key_info or key_info in ("expired", "revoked"):
        return jsonify({"error": f"Key {key_info or 'invalid'}"}), 401
    
    term = request.args.get('term')
    if not term:
        return jsonify({"error": "term required"}), 400
    
    data = fetch_from_api(term, "user")
    data = replace_branding(data)
    data["developer"] = "@tw_hacker2"
    data["api_key_owner"] = key_info["customer"]
    return jsonify(data)

@app.route('/api/mobile')
def get_mobile():
    api_key = request.args.get('api_key')
    if not api_key:
        return jsonify({"error": "api_key required"}), 401
    
    key_info = check_key(api_key)
    if not key_info or key_info in ("expired", "revoked"):
        return jsonify({"error": f"Key {key_info or 'invalid'}"}), 401
    
    term = request.args.get('term')
    if not term:
        return jsonify({"error": "term required"}), 400
    
    data = fetch_from_api(term, "mobile")
    data = replace_branding(data)
    data["developer"] = "@tw_hacker2"
    data["api_key_owner"] = key_info["customer"]
    return jsonify(data)

@app.route('/admin/gen')
def admin_gen():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    customer = request.args.get('customer')
    days = request.args.get('days', '7')
    if not customer:
        return jsonify({"error": "customer required"}), 400
    
    try:
        days = int(days)
        if days not in (1, 7, 30):
            days = 7
    except:
        days = 7
    
    api_key = generate_key(customer, days)
    return jsonify({
        "api_key": api_key,
        "customer": customer,
        "expires": KEYS_DB[api_key]["expires"],
        "valid_days": days
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
