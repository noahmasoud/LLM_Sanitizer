from flask import Blueprint, render_template, session, request
import google.generativeai as genai
import re
import json
import os

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        first_name = request.form.get("first")
        last_name = request.form.get("last")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        analyze_with_gemini(first_name, last_name, email, subject, message)
        return render_template("contact.html", in_session=session)

    else:
        return render_template("contact.html")


gemini_bp = Blueprint("gemini", __name__)
# Configure Gemini AI (Replace with your API key)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_with_gemini(first_name, last_name, email, subject, message):
    """Send user input to Gemini AI and get a bot probability score"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Analyze the following user email details and return a bot probability score from 0-100.
        If it seems human-like, return a lower score; if it looks automated, return a higher score.
        Try to be as accurate as possible. And try to look out for any SQL injection attempts.
        Check if the subject line is too generic or spammy, and check if the subject has any correlation with the message.
        Keep an eye out for any phishing attempts as well, random text, or gibberish.
      
        User Input:
        - First Name: {first_name}
        - Last Name: {last_name}
        - Email: {email}
        - Subject: {subject}
        - Message: {message}


        Respond only with a JSON object like this:
        {{
            "bot_score":
        }}
        """

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        if os.path.exists("./results/results.txt"):
            with open("./results/results.txt", "a") as file:
                file.write("\n\nEmail Content: \n")
                file.write(f"First Name: {first_name}\n")
                file.write(f"Last Name: {last_name}\n")
                file.write(f"Email: {email}\n")
                file.write(f"Subject: {subject}\n")
                file.write(f"Message: {message}\n")
                file.write(f"Gemini Response: {response_text}\n")
                file.close()
        else:
            with open("./results/results.txt", "w") as file:
                file.write(
                    "This text file contains all Gemini security checks for the contact us page.\n")
                file.write(
                    "It checks to see if the email being recieved to the company is coming from a bot or a human.\n")
                file.write(
                    "It grades it on a scale from 0-100 given a prompt to revise the email being sent. \n")
                file.write("\n\nEmail Content: \n")
                file.write(f"First Name: {first_name}\n")
                file.write(f"Last Name: {last_name}\n")
                file.write(f"Email: {email}\n")
                file.write(f"Subject: {subject}\n")
                file.write(f"Message: {message}\n")
                file.write(f"Gemini Response: {response_text}\n")
                file.close()

        # ✅ Step 1: Remove Markdown formatting if present
        # Remove Markdown fences
        cleaned_response = re.sub(r"```json|```", "", response_text).strip()

        # ✅ Step 2: Convert to JSON and extract bot_score
        parsed_response = json.loads(cleaned_response)
        # Default to 50 if missing
        bot_score = int(parsed_response.get("bot_score", 50))

        return bot_score

    except Exception as e:
        print(f"❌ Error with Gemini API: {e}")
        return 50   # Neutral score if error
