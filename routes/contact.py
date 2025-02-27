from flask import Blueprint, render_template, session

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/contact")
def contact():
    if "user" in session:
        return render_template("contact.html", in_session=session)
    else:
        return render_template("contact.html")