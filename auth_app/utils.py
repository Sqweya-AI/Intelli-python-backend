# users/utils.py
import resend
import os
from dotenv import load_dotenv
load_dotenv()

resend.api_key= os.getenv('resend_api_key')
 
first_name = 'First Name'

def send_reset_password_email(email, reset_token):
    r = resend.Emails.send({
    "from": "support@medivarse.com",
    "to": email,
    "subject": "Reset your password!",
    "html":f'<p> Hello [{first_name}  We are sorry to hear that you have been having trouble logging in on  our Intelli Concierge.\
          To resett your password, click the link below</p>' 
        f'<p>https://intelli-python-backend.onrender.com/auth/reset_password/{reset_token}</p>' 
        'You can only use this link once, not to be shared to anyone'
        '<strong> Intelli Concierge </strong>'
    })

def send_verification_email(email, verification_code):
    r = resend.Emails.send({
    "from": "support@medivarse.com",
    "to": email,
    "subject": "Verify your email!",
    "html":f'<p>Hello {first_name}.\
        Welcome to Intelli Concierge.\
        To verify your account, use the code below when prompted to enter your verification code.\
        This code is meant to not be shared to anyone'
        f'<strong> {verification_code} </strong>'  
        f'<strong> Intelli Concierge </strong>'  
    })