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
- Gemini API KEY

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
7. Setup your apikey for Gemini:
```
- Look up 'gemini api key' in desired browser
- Create account
- Get api key
- Put it in .env file as GEMINI_API_KEY

```
9. Start the application: 
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
1. Create a folder names 'results' in the main directory (it should be ignored by the gitignore).
2. Send an email using the 'Contact Us' tab in the application.
3. The LLM should scan the email contents and check to see if the sender ir a bot or spam or human.
4. The results will be sent to the 'results' folder via a .txt file.
5. There you should see every score that the LLM gave the emails.
   This is an example of the .txt file after a couple emails were sent for testing purposes:
   ```
        This text file contains all Gemini security checks for the contact us page.
        It checks to see if the email being recieved to the company is coming from a bot or a human.
        It grades it on a scale from 0-100 given a prompt to revise the email being sent. 


        Email Content: 
        First Name: botname
        Last Name: botlast
        Email: botemail@email.com
        Subject: FREEE MONEY
        Message: FRee money here!!!!
        Gemini Response: ```json
        {
            "bot_score": 95
        }
        ```


        Email Content: 
        First Name: Bot 
        Last Name: Bottery
        Email: botemail@email.com
        Subject: FREE MONEY
        Message: Get free Money here: www.getfreecash.com
        Gemini Response: ```json
        {
          "bot_score": 95
        }
        ```


        Email Content: 
        First Name: John
        Last Name: Green
        Email: johngreen@email.com
        Subject: Account Hacked
        Message: Hello you are receiving this message because your account has been hacked. Click here to unhack your account:                                 www.unhack.com
        Gemini Response: ```json
        {
          "bot_score": 85
        }
        ```


        Email Content: 
        First Name: Best
        Last Name: Buy
        Email: bestbuy@email.com
        Subject: Package delivery
        Message: Your package has been delivered. Click Here to view: www.delivery.com
        Gemini Response: ```json
        {
          "bot_score": 75
        }
        ```

        **Reasoning:**

        Several factors contribute to a higher bot score in this scenario:

        *   **Generic Email and Subject:** The email address `bestbuy@email.com` combined with the names "Best Buy" is suspicious, especially when sending out package delivery notifications. This seems like an attempt to impersonate a well-known retailer.
        *   **Generic Subject Line:** "Package delivery" is an extremely common subject line used in phishing and spam emails.
        *   **Vague Message with Link:** The message is short, vague, and contains a generic call to action with a link ("Click Here"). This is a classic phishing tactic to lure users into clicking on malicious links. Although the domain "delivery.com" is legitimate, the message itself provides no tracking number, order details, or specific information, raising suspicion.
        *   **Lack of Personalization:** A legitimate delivery notification would typically include more specific details about the package (e.g., tracking number, items, sender). The lack of personalization is a red flag.

        While "Best Buy" could theoretically be a real customer name, the combination with the email address and message content strongly suggests malicious intent and automation.


        Email Content: 
        First Name: Elvis
        Last Name: Presley
        Email: elvispresley@gmail.com
        Subject: Job Application
        Message: I have applied to this company, and would like an update on my application. Thank you!
        Gemini Response: ```json
        {
            "bot_score": 15
        }
        ```


        Email Content: 
        First Name: Amanda
        Last Name: Jones
        Email: aJones@gmail.com
        Subject: Confidential Information
        Message: Please let me know when you are available to discuss about our financial issues. Thank You!
        - Amanda
        Gemini Response: ```json
        {
          "bot_score": 15
        }
        ```
   ```
   These are some test cases that you can use, given by gemini:
   ```
           [
          {
            "email_content": {
              "first_name": "",
              "last_name": "",
              "email": "",
              "subject": "",
              "message": ""
            },
            "expected_gemini_response": {
              "bot_score": 100
            },
            "rationale": "A completely empty form is a strong indicator of a bot or automated submission."
          },
          {
            "email_content": {
              "first_name": "Susan",
              "last_name": "Smith",
              "email": "susan.smith@email.com",
              "subject": "Inquiry about your \"miracle\" product",
              "message": "I saw your advertisement for the incredible weight loss solution. Is it really true you can lose 20 pounds in a week? Where can I buy it?"
            },
            "expected_gemini_response": {
              "bot_score": 75
            },
            "rationale": "While the name and email appear normal, the use of marketing buzzwords (\"miracle,\" \"incredible\") and exaggerated claims often appear in spam emails."
          },
          {
            "email_content": {
              "first_name": "Mike",
              "last_name": "Jones",
              "email": "mike.jones@gmai.coim",
              "subject": "Question",
              "message": "I have a question about your services. Can you contact me?"
            },
            "expected_gemini_response": {
              "bot_score": 50
            },
            "rationale": "A minor typo in the email domain could be a human error, but it's also something spammers sometimes do. The generic message increases the suspicion slightly."
          },
          {
            "email_content": {
              "first_name": "Emily",
              "last_name": "Davis",
              "email": "emilydavis@email.com",
              "subject": "Website Feedback",
              "message": "I found a broken link on your website: www.yourwebsite.com/brokenlink. Thought you should know!"
            },
            "expected_gemini_response": {
              "bot_score": 20
            },
            "rationale": "Providing a specific link, even though it's part of a legitimate message, could raise the bot score slightly."
          },
          {
            "email_content": {
              "first_name": "Robert",
              "last_name": "Brown",
              "email": "robert.brown123@email.com",
              "subject": "Request for Information - Project X",
              "message": "Dear [Company Name], I am writing to inquire about your potential involvement in our upcoming project,                        \"Project X.\" We are seeking a partner with expertise in [specific area related to the company]. Our project aims to         [detailed explanation of the project]. Could you please provide me with some information on your capabilities in [specific area]?         I have attached a document with further details. Thank you for your time and consideration. Sincerely, Robert Brown"
            },
            "expected_gemini_response": {
              "bot_score": 5
            },
            "rationale": "A lengthy, detailed, and professional message with specific information is very likely to be from a human."
          }
        ]
   ```

   ## Some extra modifications
   - We fixed the file upload section to allow only the specified files to be uploaded.
   - We fixed the notes section to not allow users to view other users' notes.
     - And allowed deletion to users notes.
   - Additional schema for verified and unverified users.
   - Saw some in code vulnerabilities, like leaked api keys and set them in .env file.
