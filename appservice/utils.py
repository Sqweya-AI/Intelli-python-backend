import openai
import amadeus
from amadeus import Client, ResponseError
import os
from datetime import datetime, timedelta
import json
import re
import logging


logger = logging.getLogger(__name__)

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')  # Make sure to set this in your environment variables

# Set up Amadeus API
amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

# Keep the extract_travel_details, get_airport_code, and get_flight_offers functions as they are

def chat_with_assistant(user_message, thread_id=None):
    if thread_id is None:
        thread = openai.beta.threads.create()
        thread_id = thread.id

    message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )



    # Wait for the run to complete
    while run.status != 'completed':
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    assistant_message = messages.data[0].content[0].text.value

    return assistant_message, thread_id

def process_query(user_query, thread_id=None):
    print(f"Processing query: {user_query}")

    travel_details = extract_travel_details(user_query)

    flight_info = ""
    if travel_details['origin'] and travel_details['destination'] and travel_details['date']:
        origin_code = get_airport_code(travel_details['origin'])
        destination_code = get_airport_code(travel_details['destination'])
        
        print(f"Searching for flights from {origin_code} to {destination_code} on {travel_details['date']}")
        
        flight_offers = get_flight_offers(origin_code, destination_code, travel_details['date'])
        
        if flight_offers:
            flight_info = "Real-time flight offers:\n"
            for offer in flight_offers:
                price = offer['price']['total']
                currency = offer['price']['currency']
                airline = offer['validatingAirlineCodes'][0]
                
                departure_time = datetime.fromisoformat(offer['itineraries'][0]['segments'][0]['departure']['at'])
                arrival_time = datetime.fromisoformat(offer['itineraries'][0]['segments'][-1]['arrival']['at'])
                
                duration = arrival_time - departure_time
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                flight_info += (f"- {airline}: {price} {currency}\n"
                                f"  Departure: {departure_time.strftime('%H:%M')}\n"
                                f"  Arrival: {arrival_time.strftime('%H:%M')}\n"
                                f"  Duration: {hours}h {minutes}m\n\n")
        else:
            flight_info = "No flight offers found for the specified route and date."
    else:
        missing_info = []
        if not travel_details['origin']:
            missing_info.append("origin")
        if not travel_details['destination']:
            missing_info.append("destination")
        if not travel_details['date']:
            missing_info.append("date")
        flight_info = f"Unable to search for flights. Missing or invalid information: {', '.join(missing_info)}."

    enhanced_query = f"{user_query}\n\nExtracted travel details: {travel_details}\n\nAdditional flight information:\n{flight_info}"
    
    response, thread_id = chat_with_assistant(enhanced_query, thread_id)

    return response, thread_id


def get_airport_code(city):
    airport_codes = {
        'accra': 'ACC',
        'nairobi': 'NBO',
        'london': 'LHR',
        'new york': 'JFK',
        'paris': 'CDG',
        'tokyo': 'HND',
        'berlin': 'BER',
        'rome': 'FCO',
        'madrid': 'MAD',
        'amsterdam': 'AMS',
        'dubai': 'DXB',
        'singapore': 'SIN',
        'sydney': 'SYD',
        'los angeles': 'LAX',
        'chicago': 'ORD',
        'toronto': 'YYZ',
        'frankfurt': 'FRA',
        'istanbul': 'IST',
        'moscow': 'SVO',
        'beijing': 'PEK',
        'hong kong': 'HKG',
        'bangkok': 'BKK',
        'seoul': 'ICN',
        'mumbai': 'BOM',
        'johannesburg': 'JNB',
        'cairo': 'CAI',
        'mexico city': 'MEX',
        'sao paulo': 'GRU',
        'buenos aires': 'EZE',
        'vancouver': 'YVR',
        'montreal': 'YUL',
        'athens': 'ATH',
        'vienna': 'VIE',
        'brussels': 'BRU',
        'copenhagen': 'CPH',
        'dublin': 'DUB',
        'helsinki': 'HEL',
        'lisbon': 'LIS',
        'oslo': 'OSL',
        'prague': 'PRG',
        'stockholm': 'ARN',
        'warsaw': 'WAW',
        'zurich': 'ZRH',
        'abu dhabi': 'AUH',
        'doha': 'DOH',
        'kuala lumpur': 'KUL',
        'manila': 'MNL',
        'jakarta': 'CGK',
        'auckland': 'AKL',
        'wellington': 'WLG',
        'san francisco': 'SFO',
        'miami': 'MIA',
        'dallas': 'DFW',
        'atlanta': 'ATL',
        'boston': 'BOS',
        'washington': 'IAD',
        'seattle': 'SEA',
        'las vegas': 'LAS',
        'orlando': 'MCO',
        'honolulu': 'HNL',
        'cape town': 'CPT',
        'durban': 'DUR',
        'lagos': 'LOS',
        'addis ababa': 'ADD',
        'casablanca': 'CMN',
        'tunis': 'TUN',
        'tel aviv': 'TLV',
        'muscat': 'MCT',
        'riyadh': 'RUH',
        'jeddah': 'JED',
        'tehran': 'IKA',
        'karachi': 'KHI',
        'lahore': 'LHE',
        'colombo': 'CMB',
        'dhaka': 'DAC',
        'kathmandu': 'KTM',
        'hanoi': 'HAN',
        'ho chi minh city': 'SGN',
        'phnom penh': 'PNH',
        'yangon': 'RGN',
        'vientiane': 'VTE',
        'taipei': 'TPE',
        'shanghai': 'PVG',
        'guangzhou': 'CAN',
        'chengdu': 'CTU',
        'xian': 'XIY',
        'osaka': 'KIX',
        'fukuoka': 'FUK',
        'sapporo': 'CTS',
        'busan': 'PUS',
        'perth': 'PER',
        'brisbane': 'BNE',
        'melbourne': 'MEL',
        'adelaide': 'ADL',
        'gold coast': 'OOL',
        'christchurch': 'CHC',
        'queenstown': 'ZQN',
        'nadi': 'NAN',
        'papeete': 'PPT',
        'noumea': 'NOU',
        'port moresby': 'POM',
        'honiara': 'HIR',
        'suva': 'SUV',
        'apia': 'APW',
        'nuku alofa': 'TBU',
        'port vila': 'VLI',
        # Add more cities as needed
    }
    return airport_codes.get(city.lower(), city.upper())


def get_flight_offers(origin, destination, date):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=5  # Limit to 5 offers for brevity
        )
        logger.info(f"Successfully retrieved flight offers: {response.data}")
        return response.data
    except ResponseError as error:
        logger.error(f"Amadeus API error: {error.response.body}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_flight_offers: {str(e)}")
        return None
    
    
def extract_travel_details(text):
    origin_pattern = r'(?:from|ticket from)\s*([\w\s]+?)(?:\s+to|\s*$)'
    destination_pattern = r'(?:to|ticket to)\s*([\w\s]+)(?:\s+(?:on|next|today)|\s*$)'
    date_pattern = r'(?:on|date:?|next|today)\s*(\d{4}-\d{2}-\d{2}|\w+)'

    origin_match = re.search(origin_pattern, text, re.IGNORECASE)
    destination_match = re.search(destination_pattern, text, re.IGNORECASE)
    date_match = re.search(date_pattern, text, re.IGNORECASE)

    print(f"Origin match: {origin_match.groups() if origin_match else None}")
    print(f"Destination match: {destination_match.groups() if destination_match else None}")
    print(f"Date match: {date_match.groups() if date_match else None}")

    today = datetime.now()
    next_week = (today + timedelta(days=7)).strftime('%Y-%m-%d')

    extracted_date = today.strftime('%Y-%m-%d')
    if date_match:
        date_str = date_match.group(1)
        if date_str.lower() == 'week':
            extracted_date = next_week
        elif date_str.lower() == 'today':
            extracted_date = today.strftime('%Y-%m-%d')
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            extracted_date = date_str
        else:
            # If it's not a recognized format, keep the original string
            extracted_date = date_str

    result = {
        'origin': origin_match.group(1).strip() if origin_match else None,
        'destination': destination_match.group(1).strip() if destination_match else None,
        'date': extracted_date
    }

    print(f"Extracted travel details: {result}")
    return result

