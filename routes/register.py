from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models.user import User
from extensions import db
from functools import wraps

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
        if value and value.strip():  # mark as filled if value contains non-whitespace characters
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
        # validate additional profile fields
        ################################################################

        if validate_profile_data(form_data):
            flash("Unusual behavior detected. Registration denied.",
                  category="danger")
            return redirect(url_for("home.home"))

        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
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
