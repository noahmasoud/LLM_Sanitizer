from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.user import User
from extensions import db

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        address = request.form.get("address")
        captcha_response = request.form.get("captcha")
        stored_captcha = session.get("captcha_text")
        honeypot = request.form.get("honeypot")  # 🛑 Retrieve honeypot field

        # 🛑 Check if honeypot field is filled (bot detection)
        if honeypot:
            flash("Spam detected! Registration blocked.", "error")
            return redirect(url_for("register.register"))

        # CAPTCHA Validation
        if not stored_captcha or captcha_response.upper() != stored_captcha:
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        session.pop("captcha_text", None)

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        # Create new user and store email & address
        new_user = User(username=username)
        new_user.set_password(password)  # Hash the password before saving
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")
