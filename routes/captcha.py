from flask import Blueprint, send_file, session
from io import BytesIO
import random
import string
from utils.captcha import generate_captcha

captcha_bp = Blueprint("captcha", __name__)

def generate_random_captcha(length=6):
    """Generate a random CAPTCHA with uppercase letters, digits, and special characters"""
    characters = string.ascii_uppercase + string.digits + "!@#$%^&*"
    return ''.join(random.choices(characters, k=length))

@captcha_bp.route("/captcha/generate", methods=["GET"])
def get_captcha():
    """Generate a new CAPTCHA image with a random string"""

    captcha_text = generate_random_captcha()  # Generate a random CAPTCHA

    session['captcha_text'] = captcha_text  # Store in session for validation

    image = generate_captcha(captcha_text)  # Generate image
    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')
