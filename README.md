1-AUTH:

REGISTER
http://localhost:8000/auth/register/

VERIFY EMAIL
http://localhost:8000/auth/verify_email/

LOGIN
http://localhost:8000/auth/login/

CHANGE PASSWORD
http://localhost:8000/auth/change_password/

FORGOT PASSWORD - Request a link
http://localhost:8000/auth/forgot_password/

RESET PASSWORD
http://localhost:8000/auth/reset_password/

SEE REGISTERED USERS
http://localhost:8000/auth

PROFILE (LOGGED IN USER)
http://localhost:8000/auth/profile

DASHBOARD (MANAGERS)
http://localhost:8000/auth/dashboard

RESERVATION (ALL STAFF)
http://localhost:8000/auth/reservations



2-CHAT: (testing the prompting)

chitchat
http://localhost:8000/chat/

analysis
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
