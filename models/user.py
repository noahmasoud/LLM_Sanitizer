from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime

# Noah 2/28/2025
###########################################################
# database stored procedures
# user model
# now has a verification token and is_verified column
# verification token is used to verify user email
# is_verified is used to check if user email is verified
###########################################################


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    def set_password(self, password):
        """Hashes password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """Compares hashed password to user-provided password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
