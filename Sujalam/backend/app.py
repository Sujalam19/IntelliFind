from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_db, get_db
from auth import register_user, verify_otp
from mailer import send_match_notification
from sentence_transformers import SentenceTransformer, util
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# ===== INIT DB =====
init_db()

# ===== AI MODEL =====
model = SentenceTransformer("all-MiniLM-L6-v2")

def check_match(found_desc, category):
    conn = get_db()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT email, student_name, item_name, description
            FROM lost_items
            WHERE category = ?
        """, (category,))

        lost_items = cur.fetchall()
    finally:
        conn.close()

    found_vec = model.encode(found_desc)
    matches = []

    for email, student, item, lost_desc in lost_items:
        lost_vec = model.encode(lost_desc)
        score = util.cos_sim(found_vec, lost_vec).item()

        if score > 0.60:   # threshold
            matches.append({
                "email": email,
                "student_name": student,
                "item_name": item,
                "score": round(score, 2)
            })

    return matches

# ===== REGISTER =====
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data["name"]
    email = data["email"]

    ok, msg = register_user(name, email)
    return jsonify({"msg": msg})

# ===== LOGIN OTP =====
login_otp_store = {}

@app.route("/send-login-otp", methods=["POST"])
def send_login_otp():
    import random
    data = request.json
    otp = random.randint(100000, 999999)
    login_otp_store[data["email"]] = otp
    print(f"🔥 LOGIN OTP: {otp} -> {data['email']}")
    return jsonify({"msg": "OTP sent"})

@app.route("/verify-login-otp", methods=["POST"])
def verify_login_otp():
    data = request.json
    email = data["email"]
    otp = int(data["otp"])

    if email in login_otp_store and login_otp_store[email] == otp:
        return jsonify({"msg": "Login success"})

    return jsonify({"msg": "Invalid OTP"}), 400

# ===== LOST ITEM =====
@app.route("/lost", methods=["POST"])
def lost():
    try:
        email = request.form.get("email")
        student_name = request.form.get("student_name")
        item_name = request.form.get("item_name")
        category = request.form.get("category")
        description = request.form.get("description")
        lost_date = request.form.get("lost_date", "")
        lost_time = request.form.get("lost_time", "")
        lost_photo = request.files.get("lost_photo")

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO lost_items
                (email, student_name, item_name, category, description, lost_date, lost_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, student_name, item_name, category, description, lost_date, lost_time))
            conn.commit()
        finally:
            conn.close()

        return jsonify({"msg": "Lost item submitted successfully"})
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500

# ===== FOUND ITEM + AI MATCH =====
@app.route("/found", methods=["POST"])
def found():
    try:
        desc = request.form.get("description")
        category = request.form.get("category")
        location = request.form.get("location")
        found_date = request.form.get("found_date", "")
        found_time = request.form.get("found_time", "")
        found_photo = request.files.get("found_photo")

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO found_items(description, category, location, found_date, found_time)
                VALUES (?, ?, ?, ?, ?)
            """, (desc, category, location, found_date, found_time))
            conn.commit()
        finally:
            conn.close()

        # 🔥 AI MATCH
        matched = check_match(desc, category)

        print("🔥 AI MATCH RESULT:", matched)
        
        # Send notifications to matching lost item owners
        if matched:
            for match in matched:
                owner_email = match["email"]
                student_name = match["student_name"]
                item_name = match["item_name"]
                similarity = match["score"]
                
                # Send email notification
                print(f"📧 Sending match notification to {owner_email}")
                send_match_notification(owner_email)
                print(f"✅ Match notification sent! Item '{item_name}' found for {student_name} (Similarity: {similarity*100:.0f}%)")

        return jsonify({
            "msg": "Found item submitted",
            "matched": matched
        })
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500

# ===== SERVE FRONTEND =====
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ===== RUN SERVER =====
if __name__ == "__main__":
    app.run(debug=True)
