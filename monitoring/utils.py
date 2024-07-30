import openai 
import os 
import json

openai.api_key                     = os.getenv('OPENAI_API_KEY')
SENTIMENT_ANALYZER_ASSISTANT_ID    = os.getenv("SENTIMENT_ANALYZER_ASSISTANT_ID")

 
client = openai.OpenAI()


def sentiment_analyzer(message_list):
    thread = client.beta.threads.create()

    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id = thread.id,
        role      = "user",
        content   = message_list
    )

    # Run the Assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=SENTIMENT_ANALYZER_ASSISTANT_ID
    )

    # Retrieve the assistant's response
    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    # return assistant_response
    response = messages[0].content[0].text.value
    response = json.loads(response)
    return response



