from flask import Blueprint, render_template, request, flash, redirect, session, url_for, current_app
from models.user import User
from extensions import db, mail
import secrets
from datetime import datetime, timedelta
from flask_mail import Message

login_bp = Blueprint("login", __name__)

################################################################
# Login route - handles user authentication
################################################################


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # If your form uses username instead of email
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"\n=== Login Attempt ===")
        print(f"Username: {username}")
        print(f"Password provided: {password}")

        # Find user by username instead of email
        user = User.query.filter_by(username=username).first()
        print(f"User found: {user is not None}")

        if user:
            print(f"Username: {user.username}")
            print(f"Is verified: {user.is_verified}")
            print(f"Password hash in DB: {user.password_hash}")

            # Test password verification
            password_check = user.check_password(password)
            print(f"Password check result: {password_check}")

        if user and user.check_password(password):
            print("Password check passed")
            if not user.is_verified:
                print("User not verified")
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('login.login'))

            print("Setting user session")
            session["user"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("hub.hub"))
        else:
            if user:
                print("Password check failed")
            flash('Invalid email or password', 'danger')

    return render_template("login.html")

################################################################
# Logout route - clears user session
################################################################


@login_bp.route("/logout")
def logout():
    session.pop("user", None)
    session.pop('_flashes', None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login.login"))

###########################################################################################
# Registration route - handles new user signup with honeypot and email verification
###########################################################################################


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"\n=== Registration Data ===")
        print(f"Email: {email}")
        print(f"Username: {username}")
        print(f"Password: {password}")

        secondary_email = request.form.get('secondary_email', '')
        display_name = request.form.get('display_name', '')
        contact_number = request.form.get('contact_number', '')
        city = request.form.get('city', '')
        organization = request.form.get('organization', '')

        print("\n=== Registration Status ===")
        for field, value in [
            ('secondary_email', secondary_email),
            ('display_name', display_name),
            ('contact_number', contact_number),
            ('city', city),
            ('organization', organization)
        ]:
            print(
                f"Field: {field}\n  Value: '{value}'\n  Is Empty: {not bool(value)}")

        honeypot_triggered = any([
            secondary_email != '',
            display_name != '',
            contact_number != '',
            city != '',
            organization != ''
        ])

        if honeypot_triggered:
            print("\nRegistration DENIED - Unusual behavior detected")
            return redirect(url_for('home.home'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login.login'))

        new_user = User(
            username=username,
            email=email,
            is_verified=False
        )
        new_user.set_password(password)

        print(f"Password hash generated: {new_user.password_hash}")

        token = secrets.token_urlsafe(32)
        new_user.verification_token = token
        new_user.token_expiry = datetime.utcnow() + timedelta(hours=24)

        db.session.add(new_user)
        db.session.commit()

        send_verification_email(email, token)

        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('login.login'))

    return render_template('register.html')

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

################################################################
# Email verification route - processes verification links from emails
################################################################


@login_bp.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    print(f"Verification attempt with token: {token}")
    print(f"User found: {user is not None}")

    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('login.login'))

    if datetime.utcnow() > user.token_expiry:
        print("Token expired")
        flash('Verification link has expired. Please register again.', 'danger')
        return redirect(url_for('login.register'))

    print(f"Verifying user: {user.username}")
    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.session.commit()
    print("User verified successfully")

    flash('Your account has been verified! You can now log in.', 'success')
    return redirect(url_for('login.login'))
