# ##########################################################################################################################
# ########################################===========     1-AUTH:    ================#######################################
# ##########################################################################################################################

# ----------------------------------------------------- 1. REGISTER --------------------------------------------------------
https://intelli-python-backend.onrender.com/auth/register/ [POST]

# payload example:
{
    "first_name": "New Name",
    "last_name": "New last name",
    "role":"customer_service",
    "email": "customer_service@yahoo.com",
    "password": "123456789!"
}
# More Documentation:
-role can be changed to "IT_manager" or "department_supervisor" to register as other users other than customer_service agent







# ----------------------------------------------------- 2. VERIFY EMAIL  -----------------------------------------------------
https://intelli-python-backend.onrender.com/auth/verify_email/ [POST]

# payload example:
{
    "email":"samjosaadat@yahoo.com",
    "email_verification_token":"4e6fbc9b-46e9-43b7-aceb-e7ec47a84806"
}
# More Documentation:
--The verification token is sent in the verification email to the new registered user. Reattached back when the email is being verified (the verification link clicked)







# -----------------------------------------------------     3. LOGIN     -----------------------------------------------------
https://intelli-python-backend.onrender.com/auth/login/ [POST]

# payload example:
{
    "email": "customer_service@yahoo.com",
    "password": "123456789!"
}
# More Documentation:
-none, 






# ----------------------------------------------------- 4.CHANGE PASSWORD -----------------------------------------------------
https://intelli-python-backend.onrender.com/auth/change_password/ [POST]

# payload example:
{
    "old_password":"pasiwedi",
    "new_password":"123456789!"
}
# More Documentation:
-the verification of "new password' by inputing the new pasword twice (confirm new password) should be execute in the 
frontend








# -----------------------------------------------------     5. LOGOUT     -----------------------------------------------------
https://intelli-python-backend.onrender.com/auth/logout/
# payload example:
none? (No payload for logout?)
# More Documentation:
-logs out the current logged in user








# ----------------------------------------------------  6. FORGOT PASSWORD     -------------------------------------------------
https://intelli-python-backend.onrender.com/auth/forgot_password/ [POST]
# payload example:
{
    "email":"samjosaadat@yahoo.com"
}
# More Documentation:
- Not really, the set new password link with the reset token will be sent to the user email if it exists in the db







# ----------------------------------------------------   7. RESET PASSWORD      -------------------------------------------------
https://intelli-python-backend.onrender.com/auth/reset_password/ [POST]
# payload example:
{
    "reset_token":"41a3599e-1fd6-44c0-ac12-b481181ba76e",
    "new_password":"pasiwedi"
}
# More Documentation:
- The reset token attached was sent in the reset email







# --------------------------------------------------- 8. PROFILE (LOGGED IN USER) -------------------------------------------------
https://intelli-python-backend.onrender.com/auth/profile [GET]
# payload example:
None (No payload)
# More Documentation:
- Returns the profile of the cirrent logged in user




# ##########################################################################################################################
# ########################################===========     2-DASHBOARD:    =============#####################################
# ##########################################################################################################################


# ----------------------------------------------------    9-OVERVIEW      --------------------------------------------------------
https://intelli-python-backend.onrender.com/dashboard/overview [GET]
# payload example:
None (No payload)
# More Documentation:
- Returns the dashbaord to the current user, (different dashboards based on the user role)





# ----------------------------------------------------    10-RESERVATIONS  ------------------------------------------------------
https://intelli-python-backend.onrender.com/dashboard/reservations [GET]
# payload example:
None (No payload) 
# More Documentation:
- Returns the current available, made reservations






# ----------------------------------------------------    11-RESERVATIONS  ------------------------------------------------------
https://intelli-python-backend.onrender.com/reservations [POST]
# payload example:
{
    "first_name": "Samjo",
    "last_name": "Saadat",
    "customer_email": "kingjoe@medivarse.com",
    "customer_phone": "+233536883390",
    "number_of_adult_guests": 2,
    "number_of_child_guests": 2,
    "check_in_date": "04/01/2024", 
    "check_out_date": "04/05/2024",
    "room_type": "Standard",
    "amount_paid": 100
}
# More Documentation:
- Creates a new reservation. Should be by a new visitor, (a client to the hotel)







# ----------------------------------------------------    12-SETTINGS (USER SETTINGS)  -------------------------------------------
https://intelli-python-backend.onrender.com/dashboard/user-settings/view [GET]
# payload example:
None
# More Documentation:
- Returns the current settings specifi to the user







# ----------------------------------------------------    13-SETTINGS (USER SETTINGS)  -------------------------------------------
https://intelli-python-backend.onrender.com/user-settings/update_settings/ [PUT]
{
    "":""
}
# More Documentation:
- Sets the user settings to the newly updated ones (newly updated settings values). Not agreed yet on what should the settings include







# ----------------------------------------------------    14-SETTINGS (HOTEL SETTINGS)  -------------------------------------------
https://intelli-python-backend.onrender.com/dashboard/company-settings/view [GET]
# payload example:
None
# More Documentation:
- Returns the current settings specifi to the user







# ----------------------------------------------------    15-SETTINGS (HOTEL SETTINGS)  -------------------------------------------
https://intelli-python-backend.onrender.com/company-settings/update_settings/ [PUT]
# payload example:
{
    "":""
}
# More Documentation:
- Sets the user settings to the newly updated ones (newly updated settings values). Not agreed yet on what should the settings include







# ----------------------------------------------------------  15-BILLING -----------------------------------------------------------
https://intelli-python-backend.onrender.com/dashboard/subscribe/
# payload example:
{
     "card_number": 1234567890,
     "card_holder_name": "name",
     "expiration_date" : "tarehe",
     "cvv" : 123,
     "billing_address" : "adress",
     "zip_code" : 255,
     "country" : "country"
}
# More Documentation:
- Subscribes the currently logged in hotel  (only done/accessible to "IT_manager" role)







# ----------------------------------------------------------  15-AGENTS LIST (Employees) ------------------------------------------
https://intelli-python-backend.onrender.com/dashboard/
# payload example:
None
# More Documentation:
-Lists the registered c-service agents for now (excluding managers)






# =============CHAT================= (NOT BEING USED FOR NOW)
CHAT: (testing the prompting)

CHIT-CHAT
http://localhost:8000/chat/

ANALYSIS
http://localhost:8000/chat/analyse

TRANSLATING
http://localhost:8000/chat/analyse



























# RETELL AI'S README BELOW










# Sqweya AI Python Backend

Welcome to the Python backend repository for Sqweya AI. This demo showcases how we plan to integrate our Large Language Model (LLM) with Retell, an AI Conversational API platform.

This repository currently uses the `OpenAI` endpoint and will soon switch to the `Azure OpenAI` endpoint. Contributions are welcome to improve the stability and performance of this demo.

## Steps to Run Locally

1. Install dependencies:

```bash
pip3 install -r requirements.txt
```

2. Fill out the API keys in `.env`.

3. Use ngrok to expose the port to the public network:

```bash
ngrok http 8080
```

4. Start the websocket server:

```bash
uvicorn server:app --reload --port=8080
```

You will receive a forwarding address like `https://dc14-2601-645-c57f-8670-9986-5662-2c9a-adbd.ngrok-free.app`. Take the IP address, prepend it with `wss`, append with `/llm-websocket` path, and use it in the [Retell dashboard](https://beta.retellai.com/dashboard) to create a new agent. The agent you create should connect with your localhost.

The custom LLM URL would look like `wss://dc14-2601-645-c57f-8670-9986-5662-2c9a-adbd.ngrok-free.app/llm-websocket`.

### Future implementations: Place and Receive Phone Calls via Twilio

The `twilio_server.py` contains helper functions to utilize Twilio features for phone calls. Follow these steps:

1. Uncomment Twilio client initialization and `listen_twilio_voice_webhook(agent_id_path)` in `server.py` to set up Twilio voice webhook.

2. Put your ngrok IP address into `.env` (e.g., `https://dc14-2601-645-c57f-8670-9986-5662-2c9a-adbd.ngrok-free.app`).

3. (optional) Call `create_phone_number` to get a new number and associate it with an agent ID.

4. (optional) Call `register_phone_agent` to register your Twilio number and associate it with an agent ID.

5. (optional) Call `delete_phone_number` to release a number from your Twilio pool.

6. (optional) Call `transfer_call` to transfer an ongoing call to a destination number.

7. (optional) Call `end_call` to end an ongoing call.

8. Call `create_phone_call` to start a call with caller & callee number and your agent ID.

## Running in Production

To run in production, plug into Microsoft Azure OpenAI service(to provide the LLM service), fetch changes from this repo and then push your code to Github. Then deploy the code in a cloud environment(Azure or GCP), and use that IP to create an agent in the Retell dashboard.
