# Bokok HacksTeam Sanitizer
An Application Security Challenge Platform for Texas State University's 2025 BokoHacks

Members:
- Bryan Montoya 
- Noah Masoud 
- Nirajan Banjade

## Creativity Highlights 

Google's Gemini LLM implmentation to Sanitize user-inputs
- This checks for SQL injection, Spam Mail, Botnets, and more
- Additionaly, we used probability to determine the likelihood of the contact form request being a bot or human

Honeypot/SMTP Verification to detect spam registrations to our web application
- This idea was used to detect a bot autofilling our "additional fields" howeve humans can't see or fill the forms
- If the honey pot flags are set off, the user would be flagged and denied registration secretly
- However, if our flags are not set off, the user is "accepted" as a human but is required to verify the email for a second line of defense

Refined vulnerabilites throughout the web application
- We found vulnerabilites in the admin panel, contact form, and more
- We also found vulnerabilites in the login/register pages
- We fixed these vulnerabilites and made our application more secure

## Requirements
- Python 3.8 or higher → [Download Python](https://www.python.org/downloads/)
- Pip (Python package installer)
- SQLite → [Download SQLite](https://www.sqlite.org/download.html) (Optional if you want binaries otherwise; dependencies should install automatically)
- Modern web browser (Chrome/Firefox recommended)
- Text editor or IDE VS Code recommended → [VS Code Setup](https://code.visualstudio.com/docs/python/environments)

## Setup Instructions

5) Create and activate a virtual environment (recommended): (You can also do this through VS Code)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Mailtrap Setup
```
- Visit: https://mailtrap.io/
- Create a free account
- Click on the "Inboxes" tab
- Click on the "SMTP Settings" tab
- Copy the SMTP settings
- Paste the SMTP settings into the .env file
```
6. Setup your .env using the following format:

```
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=Your_Mailtrap_Username
MAIL_PASSWORD=Your_Mailtrap_Password
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_DEFAULT_SENDER=noreply@yourapplication.com
```
6. Start the application: 
```bash
python app.py
```


## How to test successful user registration

1. Go to the registration page
2. Register a new user
3. Check your mailtrap inbox for email for a verification link
4. Click the link to verify your email
5. Login to the application

### How to test Honeypot/SMTP Verification

1. Go to the registration page
2. Register a new user
3. Attempt login with the user you just registered
- You will not be able to login because the email was not verified
4. Check your mailtrap inbox for email for a verification link
4. Click the link to verify your email
5. Login to the application
- after clicking the link, you should be able to login

### How to test Honey Pot Fields 

1. Go to templates/register.html
2. Replace lines 54-55 with the following code:
```
<div class="additional-profile-section" 
        style="position: absolute; left: -1px; visibility: visible; height: 0; overflow: visible;">
```
3. Enter a valid email and password
4. Populate any of the honeypot fields with dummy data
5. Click register
- You will be redirected to the login page 
- You should see in your terminal the log of the honey pot flags being triggered
- if any of these are populated, the user is automatticly flagged and denied registration

```
Example of what you should see in your terminal:

=== Registration Data ===
Email: honeypottest@gmail.com
Username: honeyPot
Password: HoneyPOt12345$

=== Registration Status ===
Field: secondary_email
  Value: ''
  Is Empty: True
Field: display_name
  Value: ''
  Is Empty: True
Field: contact_number
  Value: '12345'
  Is Empty: False
Field: city
  Value: 'Florida'
  Is Empty: False
Field: organization
  Value: 'Txst'
  Is Empty: False
```


4. Check your mailtrap inbox for email for a verification link
5. It will not be sent because the honey pot fields were triggered



### How to test Gemini LLM Sanitization
1.