from flask import Blueprint, render_template, session, request
import google.generativeai as genai
import re
import json
import os

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/contact", methods=["GET","POST"])
def contact():
    if "user" in session:
        if request.method == "POST":
            first_name=request.form.get("first")
            last_name=request.form.get("last")
            email=request.form.get("email")
            subject=request.form.get("subject")
            message=request.form.get("message")
            analyze_with_gemini(first_name, last_name, email, subject , message)
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
       print(f"🔍 Raw Gemini response: {response_text}")  # Debugging


       # ✅ Step 1: Remove Markdown formatting if present
       cleaned_response = re.sub(r"```json|```", "", response_text).strip()  # Remove Markdown fences


       # ✅ Step 2: Convert to JSON and extract bot_score
       parsed_response = json.loads(cleaned_response)
       bot_score = int(parsed_response.get("bot_score", 50))  # Default to 50 if missing


       return bot_score


   except Exception as e:
       print(f"❌ Error with Gemini API: {e}")
       return 50   # Neutral score if error


