from flask import Blueprint, render_template, request, flash, redirect, session, url_for, current_app
from models.user import User
from extensions import db, mail
import secrets
from datetime import datetime, timedelta
from flask_mail import Message

login_bp = Blueprint("login", __name__)

################################################################
# login route that will handle user authentication
################################################################


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('login.login'))

            session["user"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("hub.hub"))
        else:
            flash('Invalid username or password', 'danger')

    return render_template("login.html")

################################################################
# Registration route that handles new user signup with email verification
################################################################


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

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

        token = secrets.token_urlsafe(32)
        new_user.verification_token = token
        new_user.token_expiry = datetime.utcnow() + timedelta(hours=24)

        db.session.add(new_user)
        db.session.commit()

        send_verification_email(email, token)

        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('login.login'))

    return render_template('register.html')

##########################################################################
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

##########################################################################
# verification route that will processes verification links from emails
# verify user email and set is_verified to true
##########################################################################


@login_bp.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('login.login'))

    # this function checks if the verification link has expired
    if datetime.utcnow() > user.token_expiry:
        flash('Verification link has expired. Please register again.', 'danger')
        return redirect(url_for('login.register'))

    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.session.commit()

    # this redirects the user back to login page after verification
    flash('Your account has been verified! You can now log in.', 'success')
    return redirect(url_for('login.login'))
