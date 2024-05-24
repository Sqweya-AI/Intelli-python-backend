# users/utils.py
import resend
import os
from dotenv import load_dotenv
load_dotenv()

resend.api_key= os.getenv('resend_api_key')


def send_reset_password_email(email, reset_token):
    r = resend.Emails.send({
    "from": "support@medivarse.com",
    "to": email,
    "subject": "Reset your password!",
    "html":f'<p><strong>Pasword Reset </strong> link for <strong {'variable'} </strong></p>' 
        f'<p>{reset_token}</p>' 
        '<strong>Rapid Rabbit </strong>'
    })

def send_verification_email(email, verification_code):
    r = resend.Emails.send({
    "from": "support@medivarse.com",
    "to": email,
    "subject": "Verify your email!",
    "html":f'<p><strong>Email verification</strong> code \
        <strong> {'variable'} </strong></p>' 
        f'<p>{verification_code}</p>' 
        '<strong>Rapid Rabbit </strong>'
    })