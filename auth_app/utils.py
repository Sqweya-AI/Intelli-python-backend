# users/utils.py
from django.core.mail import send_mail

def send_reset_password_email(email, reset_token):
    # # Implement your logic to send reset password email
    # # This can be done using Django's send_mail function or any other email sending method
    # # Example using Django's send_mail:
    # subject = 'Password Reset Request'
    # message = f'Use the following link to reset your password: /reset-password/{reset_token}'
    # from_email = 'your@example.com'  # Change to your email address
    # recipient_list = [email]
    # send_mail(subject, message, from_email, recipient_list)
    print('')
    print(f'Password reset link has been sent to {email}.  Reset token: {reset_token}')
    print('')

def send_verification_email(email, verification_token):
    # # Implement your logic to send verification email
    # # This can be done using Django's send_mail function or any other email sending method
    # # Example using Django's send_mail:
    # subject = 'Email Verification'
    # message = f'Use the following link to verify your email: /verify-email/{verification_token}'
    # from_email = ''your@example.com''  # Change to your email address
    print('')
    print(f'Confirmation  link has been sent to {email}.  With token: {verification_token}')
    print('')