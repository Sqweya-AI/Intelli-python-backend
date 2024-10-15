import os 
import requests
import json 
from amadeus import Client, ResponseError
from datetime import datetime
import json
from decouple import config
from openai import OpenAI
import time
from typing import List, Dict, Any


ASSISTANT_ID   = config('FLIGHT_ASSISTANT_ID')
OPENAI_API_KEY = config('OPENAI_API_KEY')


client    = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)


# Set up Amadeus API
amadeus = Client(
    client_id=config('AMADEUS_ID'),
    client_secret=config('AMADEUS_SECRET')
)



# iata code assistant 
iata_code_assistant = config('iata_code_assistant')
assistant_iata = client.beta.assistants.retrieve(assistant_id=iata_code_assistant)

def get_iata_city_code(city):
    thread = client.beta.threads.create()
    thread_id = thread.id 

    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id = thread_id,
        role      = "user",
        content   = city
    )

    # Run the Assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_iata.id
    )

    # Retrieve the assistant's response
    messages = list(client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id))

    # return assistant_response
    response = messages[0].content[0].text.value
    response = json.loads(response)
    return response


def extract_flight_info(offer):
    flight_info = {
        "id": offer["id"],
        "price": offer["price"]["total"],
        "currency": offer["price"]["currency"],
        "departure": [],
        "arrival": [],
        "duration": [],
        "airline": [],
        "stops": []
    }
    
    for itinerary in offer["itineraries"]:
        for segment in itinerary["segments"]:
            flight_info["departure"].append({
                "airport": segment["departure"]["iataCode"],
                "time": segment["departure"]["at"]
            })
            flight_info["arrival"].append({
                "airport": segment["arrival"]["iataCode"],
                "time": segment["arrival"]["at"]
            })
            flight_info["duration"].append(segment["duration"])
            flight_info["airline"].append(segment["carrierCode"])
            flight_info["stops"].append(segment.get("numberOfStops", 0))
    
    return flight_info




def get_flight_offers(origin, destination, date):
    cities_codes = get_iata_city_code(f'from {origin} to {destination}')
    origin       = cities_codes['origin']['code']
    destination  = cities_codes['destination']['code']
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=3
        )
        # Extract information for all flight offers
        flight_offers = [extract_flight_info(offer) for offer in response.data]
        return flight_offers
    except ResponseError as error:
        print(f"An error occurred: {error}")
        return None


def process_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    print('the tools are being used')
    tool_outputs = []
    for action in tool_calls:
        func_name = action['function']['name']
        arguments = json.loads(action['function']['arguments'])

        if func_name == "get_flights_prices":
            output = get_flights_prices(
                origin=arguments['origin'],
                destination=arguments['destination'],
                date=arguments['date']
            )
            tool_outputs.append({
                "tool_call_id": action['id'],
                "output": output
            })
        else:
            raise ValueError(f"Unknown function: {func_name}")

    return tool_outputs



def get_flights_prices(origin: str, destination: str, date: str) -> str:
    response = get_flight_offers(origin, destination, date)
    return json.dumps(response)




def handle_flight_prices(message: str, thread_id: str | None) -> str:
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id 
    
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    while True:
        time.sleep(3)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

        if run_status.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            return messages.data[0].content[0].text.value

        elif run_status.status == 'requires_action':
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            tool_outputs = process_tool_calls(required_actions["tool_calls"])

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )





# Example usage
# print(handle_flight_prices('Hello I am Kaba !', None))
# print(handle_flight_prices('Hello I want to travels from accra to dakar', None))
# print(handle_flight_prices('Yes I want to travels from accra to dakar on 15 december 2024', None))