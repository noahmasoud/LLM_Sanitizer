# from flask import Blueprint, render_template, request, flash, redirect, url_for, session
# from models.user import User
# from extensions import db

# register_bp = Blueprint("register", __name__)

# @register_bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")
#         email = request.form.get("email")
#         address = request.form.get("address")
#         captcha_response = request.form.get("captcha")
#         stored_captcha = session.get("captcha_text")
#         honeypot = request.form.get("honeypot")  # 🛑 Retrieve honeypot field

#         # 🛑 Check if honeypot field is filled (bot detection)
#         if honeypot:
#             flash("Spam detected! Registration blocked.", "error")
#             return redirect(url_for("register.register"))

#         # CAPTCHA Validation
#         if not stored_captcha or captcha_response.upper() != stored_captcha:
#             flash("Invalid CAPTCHA. Please try again.", "error")
#             return redirect(url_for("register.register"))

#         session.pop("captcha_text", None)

#         # Check if the username already exists
#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash("Username already exists. Please choose a different one.", "error")
#             return redirect(url_for("register.register"))

#         # Create new user and store email & address
#         new_user = User(username=username)
#         new_user.set_password(password)  # Hash the password before saving
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Registration successful! You can now log in.", "success")
#         return redirect(url_for("login.login"))

#     return render_template("register.html")
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.user import User
from extensions import db
import google.generativeai as genai

register_bp = Blueprint("register", __name__)

# ✅ Configure Gemini AI (Replace with your API key)
genai.configure(api_key="API_KEY_HERE")

def analyze_with_gemini(username, password, email, address, captcha_response):
    """Send user input to Gemini AI and get a bot probability score"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Analyze the following user registration details and return a bot probability score (0-100). 
        If it seems human-like, return a lower score; if it looks automated, return a higher score.
        
        User Input:
        - Username: {username}
        - Password: {password}
        - Email: {email}
        - Address: {address}
        - CAPTCHA Response: {captcha_response}

        Return only a JSON object with a single key 'bot_score' between 0 and 100.
        """

        response = model.generate_content(prompt)
        return int(response.text.strip().split(":")[-1].replace("}", "").strip())  # Extract score
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return 50  # Neutral score if error

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # ✅ Extract user inputs
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        address = request.form.get("address")
        captcha_response = request.form.get("captcha")
        stored_captcha = session.get("captcha_text")
        honeypot = request.form.get("honeypot")  # 🛡️ Bot detection field

        # 🛡️ Check honeypot field (if filled, it's a bot)
        if honeypot:
            flash("Spam detected! Registration blocked.", "error")
            return redirect(url_for("register.register"))

        # 🛡️ CAPTCHA Validation
        if not stored_captcha or captcha_response.upper() != stored_captcha:
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        session.pop("captcha_text", None)  # Remove CAPTCHA after use

        # 🔥 **Step 1: Send input to Gemini AI**
        bot_score = analyze_with_gemini(username, password, email, address, captcha_response)

        # 🔥 **Step 2: Block if the score is too high (e.g., ≥ 70)**
        print("Bot score is : ",bot_score)
        if bot_score >= 30:
            flash(f"Potential bot detected! Score: {bot_score}. Registration blocked.", "error")
            return redirect(url_for("register.register"))

        # ✅ Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        # ✅ Create new user
        new_user = User(username=username)
        new_user.set_password(password)  # Hash password
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")
