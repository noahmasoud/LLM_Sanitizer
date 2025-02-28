from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.user import User
from extensions import db, mail
from functools import wraps
import secrets
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app

register_bp = Blueprint("register", __name__)

################################################################
# Debug mode flag - set to False in production
# To turn off debugging featuure set to false
################################################################
DEBUG_MODE = True


class AdditionalField:
    def __init__(self, name):
        self.name = name
        self.is_empty = True

    def check_value(self, value):
        """Check if optional field was filled and update status"""
        if value and value.strip():  # Only mark as filled if value contains non-whitespace characters
            self.is_empty = False
        return self.is_empty


################################################################
# Debug function to print field statuses
################################################################

def debug_print_status(form_data, fields, bot_detected):
    if not DEBUG_MODE:
        return
    print("\n=== Registration Status ===")
    for field_name, field in fields.items():
        if field_name in form_data:
            print(f"Field: {field_name}")
            print(f"  Value: '{form_data[field_name]}'")
            print(f"  Is Empty: {field.is_empty}")
    print(
        f"\nRegistration {'DENIED - Unusual behavior detected' if bot_detected else 'ALLOWED'}")
    print("============================\n")


################################################################
# initialize additional profile fields with status tracking
################################################################
ADDITIONAL_FIELDS = {
    'secondary_email': AdditionalField('secondary_email'),
    'display_name': AdditionalField('display_name'),
    'contact_number': AdditionalField('contact_number'),
    'city': AdditionalField('city'),
    'organization': AdditionalField('organization')
}

################################################################
# Validate additional profile fields and update their status
# Returns True if any optional field was unexpectedly filled
################################################################


def validate_profile_data(form_data):
    bot_detected = False
    for field_name, field in ADDITIONAL_FIELDS.items():
        if field_name in form_data:
            is_empty = field.check_value(form_data[field_name])
            if not is_empty:
                bot_detected = True
    debug_print_status(form_data, ADDITIONAL_FIELDS, bot_detected)
    return bot_detected


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_data = request.form.to_dict()

        ################################################################
        # validate additional profile fields (honeypot)
        ################################################################
        if validate_profile_data(form_data):
            # Honeypot triggered - silently redirect to home
            # We don't want to alert bots that we detected them
            return redirect(url_for("home.home"))

        # If honeypot not triggered, proceed with normal registration
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        captcha_response = request.form.get("captcha")
        stored_captcha = session.get("captcha_text")

        if not stored_captcha or captcha_response.upper() != stored_captcha:
            flash("Invalid CAPTCHA. Please try again.", "error")
            return redirect(url_for("register.register"))

        session.pop("captcha_text", None)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login.login"))

        # Create new user with unverified status
        new_user = User(
            username=username,
            email=email,
            is_verified=False
        )
        new_user.set_password(password)

        # Generate verification token
        token = secrets.token_urlsafe(32)
        new_user.verification_token = token
        new_user.token_expiry = datetime.utcnow() + timedelta(hours=24)

        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        send_verification_email(email, token)

        flash("Registration successful! Please check your email to verify your account.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")

################################################################
# Email verification helper - sends verification email to new users
################################################################


def send_verification_email(email, token):
    verification_url = url_for(
        'login.verify_email', token=token, _external=True)

    msg = Message(
        'Verify Your Account',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )

    msg.body = f'''Please verify your account by clicking the following link:
{verification_url}

If you did not register for this account, please ignore this email.

This link will expire in 24 hours.
'''

    msg.html = f'''
<p>Please verify your account by clicking the following link:</p>
<p><a href="{verification_url}">Verify Your Account</a></p>
<p>If you did not register for this account, please ignore this email.</p>
<p>This link will expire in 24 hours.</p>
'''

    mail.send(msg)
