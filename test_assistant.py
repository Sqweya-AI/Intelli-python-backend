from openai import OpenAI
from decouple import config


client = OpenAI(api_key=config('OPENAI_API_KEY'))

vector_store = client.beta.vector_stores.retrieve(
  vector_store_id="vs_gJaLCbIBOfSEGqhgwiFWsgrz"
)

print(vector_store.id)

assistant = client.beta.assistants.update(
  assistant_id=config('ASSISTANT_ID'),
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)