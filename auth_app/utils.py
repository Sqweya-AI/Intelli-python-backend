# users/utils.py
import resend
import os
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv('resend_api_key')

first_name = 'First Name'
inviter_name = 'Inviter\'s Name'
company_name = 'Company Name'

def send_reset_password_email(email, reset_token):
    r = resend.Emails.send({
        "from": "support@medivarse.com",
        "to": email,
        "subject": "Reset your password!",
        "html": f'''
            <p>Hello {first_name},</p>
            <p>We are sorry to hear that you have been having trouble logging in to our Intelli Concierge.</p>
            <p>To reset your password, click the link below:</p>
            <p><a href="https://intelli-python-backend.onrender.com/auth/reset_password/{reset_token}">Reset Password</a></p>
            <p>You can only use this link once. Do not share it with anyone.</p>
            <strong>Intelli Concierge</strong>
        '''
    })

def send_verification_email(email, verification_code):
    r = resend.Emails.send({
        "from": "support@medivarse.com",
        "to": email,
        "subject": "Verify your email!",
        "html": f'''
            <p>Hello {first_name},</p>
            <p>Welcome to Intelli Concierge.</p>
            <p>To verify your account, use the code below when prompted to enter your verification code. Do not share this code with anyone.</p>
            <strong>{verification_code}</strong>
            <strong>Intelli Concierge</strong>
        '''
    })

def send_invite_email(email, default_password):
    r = resend.Emails.send({
        "from": "support@medivarse.com",
        "to": email,
        "subject": "You are invited to join the team",
        "html": f'''
            <p>Hello {first_name},</p>
            <p>{inviter_name} has invited you to join the customer service team at {company_name}.</p>
            <p>Your login details are below:</p>
            <p>Email: {email}</p>
            <p>Password: <strong>{default_password}</strong></p>
            <p>Welcome to <strong>Intelli Concierge</strong></p>
        '''
    })
