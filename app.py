import datetime
from flask import Flask, jsonify, render_template, request, session
from psycopg2 import Error
from auth import auth_bp, get_db_connection
from tinyllama import tinyllama_bp
from gemma import gemma_bp  # Updated import
from werkzeug.security import generate_password_hash


app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(tinyllama_bp, url_prefix='/chat')
app.register_blueprint(gemma_bp, url_prefix='/chat')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/faq')
def faq():
    return render_template('faq.html')
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')



@app.route("/get_user_info/<int:user_id>", methods=["GET"])
def get_user_info(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, email, password_hash FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return jsonify({
            "username": user[0],
            "email": user[1],
            "password": user[2]
        })
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/update_user_info/<int:user_id>", methods=["POST"])
def update_user_info(user_id):
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if password.strip() != "":
         
        password_hash = generate_password_hash(password)
    else:
        password_hash = None
    conn = get_db_connection()
    cur = conn.cursor()
    if password_hash:
        cur.execute("""
            UPDATE users
            SET username = %s, email = %s, password_hash = %s
            WHERE user_id = %s
        """, (username, email, password_hash, user_id))
    else:
        cur.execute("""
            UPDATE users
            SET username = %s, email = %s
            WHERE user_id = %s
        """, (username, email, user_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True})




@app.route("/submit_feedback/<int:userid>", methods=["POST"])
def submit_feedback(userid):
    data = request.get_json()
    rating = data.get("rating")
    comments = data.get("comments")  

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (user_id, rating, comments, submitted_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
    """, (userid, rating, comments))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True})

@app.route("/delete_user/<int:userid>", methods=["POST"])
def delete_user(userid):

    if not userid:
        return jsonify({"error": "User not logged in"}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete user and optionally related messages or conversations
        cur.execute("DELETE FROM users WHERE user_id = %s", (userid,))
        conn.commit()

        cur.close()
        conn.close()

        # Clear the session after deletion
        session.clear()
        
        return jsonify({"success": True, "message": "User deleted and logged out."})
    
    except Exception as e:
        print("Error deleting user:", e)
        return jsonify({"error": "Failed to delete user"}), 500
    
    




if __name__ == '__main__':
    app.run(debug=True)