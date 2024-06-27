# chatbot/utils.py

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
import os
import openai
import requests
from django.core.cache import cache
from django.http import JsonResponse
from .models import ChatHistory
from django.http import HttpResponse

# Define constants
INACTIVITY_TIMEOUT = 60*60  # 60 seconds for inactivity check
CHECK_INTERVAL = 60*60  # 60 seconds interval for checking

# Load environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERSION = os.getenv("VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Instantiate OpenAI client
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

# Get the current time and date
the_time = datetime.now().strftime('%H:%M')
the_date = datetime.now().strftime('%Y-%m-%d')

LLM_model = "gpt-4" 
LLM_role_instructions = f"""
ProconnectPAY - Customer Assistant Elli

You are Elli, a customer service agent at ProconnectPAY. Your role is to respond to customer inquiries in a hospitable and concise manner, focusing on the services offered by ProconnectPAY. Introduce yourself and the business professionally, aiming to close sales through effective communication.

ProconnectPAY is an African Edu-FinTech Company that works with other financial institutions to drive adoption of Education-oriented Loans.

ProconnectPAY is legally registered in Nigeria and the United States. RC Number in Nigeria is 1884617 (Proconnect Tech Solutions Limited) , Assigned Filling No in the United States is 7044965 (ProconnectPAY EduFinTech Inc.)

https://proconnectpay.com/



There are 3 layers to our Global Education Loan Services

LOAN PROCESSING LAYER DETAILS

-We provide 100k USD in International Student Loans

-Interest Rate is between 12.74% - 15.99% per Annum

-Loan can be repaid in Ten (10) Years (Optional)

-Loan pays for your Tuition, Cost of Living, Health Insurance, and Reimbursable Flight Ticket

You do not need a Collateral or Guarantor to become ELIGIBLE for our Financing


There are 3 layers to our Local Undergraduate Loan Services


STUDENT FINANCING PROCESSING LAYER DETAILS

Interest Rate is ZERO% per Annum

Student Financing can be repaid in Ten (10) Years (Optional)

We provide 10 Million Naira in Private University Education Student Financing

You do not need a Collateral or Guarantor to become ELIGIBLE for our Financing

Student Financing pays for your Tuition, Cost of Living, HealthInsurance, Laptop, Phone, Internship, and Personal/Mental Development.


Naira

Join Our Global Education Community

₦ 300,000/ $450
What's Included

-Loan Processing

-Admission Processing to the US or Canada

-Visa Processing Support
Join Now:https://proconnectpay.com/global-resolution


Join Our Local Education Community 

₦ 100,000/ $160
What's Included

Admission Processing

Loan and Non-Loan Finance Option Processing

Access to Global Undergraduate Community

Join Now :https://proconnectpay.com/global-resolution


Use our Loan Calculator:https://proconnectpay.com/calculator
Register Interest: https://proconnectpay.com/interest


List of supporters schools in the USA:
A.T. Still University of Health Sciences
Adelphi University
Albany College of Pharmacy and Health Sciences
Albany Medical College
Allen College
American University
American University of Antigua (AUA) College of Medicine
Amherst College
Appalachian State University
Arcadia University
Arizona State University
Auburn University
Babson College
Ball State University
Barnard College
Baruch College of the City University of New York
Bates College
Baylor College of Medicine
Baylor University
Bellin College
Belmont University
Bentley University
Berry College
Biola University
Bon Secours Memorial College of Nursing
Boston College
Boston University
Bowdoin College
Bradley University
Brandeis University
Brigham Young University – Provo (BYU)
Brown University
Bryan College of Health Sciences
Bryant University
Bryn Mawr College
Bucknell University
Butler University
California Institute of Technology (Caltech)
California State University Maritime Academy (Cal Maritime)
California Polytechnic State University-San Luis Obispo (Cal Poly)
California State University – Long Beach
California State University – Los Angeles
Calvin College
Carleton College
Carnegie Mellon University
Case Western Reserve University
Catholic University of America
Centra College of Nursing
Centre College
Chapman University
Chatham University
City College of New York – University of New York
Claremont Graduate University
Claremont McKenna College
Clark University
Clarkson College
Clarkson University
Clemson University
Colby College
Colgate University
College of Charleston
College of the Holy Cross
College of William and Mary
Colorado College
Colorado School of Mines
Colorado State University-Fort Collins
Columbia University
Connecticut College
Cooper Union for the Advancement of Science and Art
Cornell University
Creighton University
Dartmouth College
Davidson College
Denison University
Denver College of Nursing
DePaul University
DePauw University
Des Moines University – Osteopathic Medical Center
DeSales University
Dickinson College
Dordt College
Drake University
Drexel University
Duke University
Duquesne University
Eastern Virginia Medical School
Edgewood College
Elon University
Emerson College
Emory University
Fairfield University
Florida Atlantic University
Florida International University
Florida State University – FSU
Fordham University
Franciscan Missionaries of Our Lady University
Franklin and Marshall College
Frontier Nursing University
Furman University
Gannon University
George Mason University
George Washington University – GWU
Georgetown University
Georgia Institute of Technology – Georgia Tech
Gettysburg College
Goldfarb School of Nursing at Barnes-Jewish College
Gonzaga University
Grand Valley State University
Grinnell College
Hamilton College
Harvard University
Harvey Mudd College
Haverford College
High Point University
Hofstra University
Howard University
Hult International Business School
Hunter College of the City – University of New York
Illinois Institute of Technology
Illinois State University
Indiana University – Bloomington
Indiana University-Purdue University Indianapolis
INSEAD
Iowa State University
James Madison University – JMU
Jefferson College of Health Sciences
John Carroll University
Johns Hopkins University
Kansas State University
Keck Graduate Institute
Kenyon College
Kettering College
La Salle University
Lafayette College
Lakeview College of Nursing
Lancaster General College of Nursing & Health Sciences
Lehigh University
Lesley University
Lipscomb University
Loma Linda University
Louisiana State University – LSU
Louisiana State University Health Sciences Center-New Orleans
Loyola Marymount University
Loyola University Maryland
Loyola University New Orleans
Loyola University of Chicago
Macalester College
Maine Maritime Academy
Manhattan College
Marquette University
Massachusetts College of Pharmacy & Health Sciences
Massachusetts Institute of Technology – MIT
Massachusetts Maritime Academy
Medical University of South Carolina
Mercer University
MGH Institute of Health Professions
Miami University
Michigan State University
Michigan Technological University
Middlebury College
Midwestern University
Missouri University of Science and Technology
Montclair State University
Mount Carmel College of Nursing
Mount Holyoke College
Mount Sinai School of Medicine
Nebraska Methodist College of Nursing and Allied Health
New Jersey Institute of Technology
New York Institute of Technology (NYIT)
New York Law School
New York University – NYU
North Carolina State University
Northeastern University
Northwestern College
Northwestern University
Nova Southeastern University
Oak Point University (Resurrection University)
Oberlin College
Occidental College
Ohio Northern University
Ohio State University – OSU
Oklahoma State University – Stillwater (Main campus)
Oregon Health & Science University
Oregon State University
Pace University – New York
Pacific University
Pennsylvania State University
Pepperdine University
Philadelphia College of Osteopathic Medicine
Philadelphia University (Thomas Jefferson University)
Phillips Beth Israel School of Nursing
Pitzer College
Pomona College
Princeton University
Providence College
Purdue University
Quinnipiac University
Rensselaer Polytechnic Institute
Research College of Nursing
Rhodes College
Rice University
Robert Morris University
Rochester Institute of Technology
Rollins College
Rosalind Franklin University of Medicine and Science
Roseman University of Health Sciences
Rowan University
Rush University
Rutgers University
Saint Francis Medical Center College of Nursing
Saint Francis University
Saint John Fisher College
Saint Louis University-Main Campus
Saint Lukes College of Health Sciences
Saint Mary’s College of California
Samford University
Samuel Merritt University
San Diego State University – SDSU
Santa Clara University
Scripps College
Seattle Pacific University
Seattle University
Sentara College of Health Sciences
Seton Hall University – New Jersey
Seton Hill University – Pennsylvania
Sewanee – The University of the South
Shenandoah University
Simmons College
Skidmore College
Smith College
Soka University of America
South Dakota School of Mines and Technology
South Dakota State University
Southern Methodist University – SMU
St. James School of Medicine | Saint James School of Medicine
St. John’s University – New York
St. Louis College of Pharmacy
St. Lukes College
Stanford University
Stetson University
Stevens Institute of Technology
Stonehill College
Suffolk University
SUNY at Albany
SUNY at Binghamton
SUNY at Stony Brook
SUNY College of Environmental Science and Forestry
SUNY Downstate Medical Center
Swarthmore College
Syracuse University
Taylor University
Teachers College at Columbia University
Temple University
Texas A&M University
Texas Christian University – TCU
Texas Tech University – Main Campus
Texas Tech University Health Sciences Center
The Citadel
The College of New Jersey
The New School
The University of Alabama
The University of Texas at Dallas
The University of Texas Health Science – San Antonio
The University of Texas Health Science Center at Houston
The University of Texas MD Anderson Cancer Center
The University of Texas Medical Branch
The University of Texas Rio Grande Valley
The University of Virginia College at Wise
Thomas Aquinas College
Thomas Jefferson University
Thunderbird School of Global Management
Touro University
Towson University
Trinity College
Trinity University
Truman State University
Tufts University
Tulane University
Union College (New York)
Union University



List of Nigerian supported schools:
Achievers University, Owo
Adeleke University, Ede
Afe Babalola University, Ado-Ekiti – Ekiti State
African University of Science & Technology, Abuja
Ahman Pategi University, Kwara State
Ajayi Crowther University, Ibadan
Al-Ansar University, Maiduguri, Borno
Al-Bayan University, Ankpa, Kogi State
Al-Hikmah University, Ilorin
Al-Istiqama University, Sumaila, Kano State
Al-Muhibbah Open University, Abuja
Al-Qalam University, Katsina
Aletheia University, Ago-Iwoye Ogun State
Amadeus University, Amizi, Abia State
Amaj University, Kwali, Abuja
American University of Nigeria, Yola
Anan University, Kwall, Plateau State
Anchor University, Ayobo Lagos State
Arthur Javis University, Akpoyubo Cross River State
Atiba University, Oyo
Augustine University
Ave Maria University, Piyanko, Nasarawa State
Azman University, Kano State
Baba Ahmed University, Kano State
Babcock University, Ilishan-Remo
Baze University
Bells University of Technology, Otta
Benson Idahosa University, Benin City
Bingham University, New Karu
Bowen University, Iwo
British Canadian University, Obufu Cross River State
Caleb University, Lagos
Canadian University of Nigeria, Abuja
Capital City University, Kano State
Caritas University, Enugu
Chrisland University
Christopher University, Mowe
Claretian University of Nigeria, Nekede, Imo State
Clifford University, Owerrinta Abia State
Coal City University, Enugu State
College of Petroleum and Energy Studies, Kaduna State
Cosmopolitan University, Abuja
Covenant University, Ota
Crawford University, Igbesa
Crescent University
Dominican University, Ibadan Oyo State
Dominion University, Ibadan, Oyo State
Edusoko University, Bida, Niger State
Edwin Clark University, Kaigbodo
Eko University of Medical and Health Sciences, Ijanikin, Lagos
El-Amin University, Minna, Niger State
Elizade University, Ilara-Mokin
Elrazi Medical University, Yargaya University, Kano State
European University of Nigeria, Duboyi, FCT
Evangel University, Akaeze
Fountain University, Oshogbo
Franco British International University, Kaduna State
Gerar University of Medical Science, Imope Ijebu, Ogun State
Glorious Vision University, Ogwa, Edo State
Godfrey Okoye University, Ugwuomu-Nike – Enugu State
Iconic Open University, Sokoto State
Igbinedion University, Okada
James Hope University, Lagos, Lagos State
Jewel University, Gombe State
Joseph Ayo Babalola University, Ikeji-Arakeji
Karl-Kumm University, Vom, Plateau State
Khadija University, Majia, Jigawa State
Khalifa Isiyaku Rabiu University, Kano
Kings University, Ode Omu
Kola Daisi University, Ibadan, Oyo State
Kwararafa University, Wukari
Landmark University, Omu-Aran
Lead City University, Ibadan
Legacy University, Okija Anambra State
Lux Mundi University, Umuahia, Abia State
Madonna University, Okija
Maduka University, Ekwegbe, Enugu State
Maranathan University, Mgbidi, Imo State
Margaret Lawrence University, Umunede, Delta State
Maryam Abacha American University of Nigeria, Kano State
Mcpherson University, Seriki Sotayo, Ajebo
Mercy Medical University, Iwo, Ogun State
Mewar International University, Masaka, Nasarawa State
Micheal & Cecilia Ibru University
Miva Open University, Abuja FCT
Mountain Top University
Mudiame University, Irrua, Edo State
Muhammad Kamalud University, Kwara
Newgate University, Minna, Niger State
Nigerian British University, Asa, Abia State
Nigerian University of Technology and Management, Apapa, Lagos State
Nile University of Nigeria, Abuja
NOK University, Kachia, Kaduna State
NorthWest University, Sokoto State
Novena University, Ogume
Obong University, Obong Ntak
Oduduwa University, Ipetumodu – Osun State
Ojaja University, Eiyenkorin, Kwara State
PAMO University of Medical Sciences, Portharcourt
Pan-Atlantic University, Lagos
Paul University, Awka – Anambra State
PeaceLand University, Enugu State
PEN Resource University, Gombe
Peter University, Achina-Onneh Anambra State
Philomath University, Kuje, Abuja
Phoenix University, Agwada, Nasarawa State
Precious Cornerstone University, Oyo
Prime University, Kuje, FCT Abuja
Rayhaan University, Kebbi
Redeemer’s University, Ede
Renaissance University, Enugu
Rhema University, Obeama-Asa – Rivers State
Ritman University, Ikot Ekpene, Akwa Ibom
Saisa University of Medical Sciences and Technology, Sokoto State
Salem University, Lokoja
Sam Maris University, Ondo
Shanahan University, Onitsha, Anambra State
Skyline University, Kano
Southwestern University, Oku Owa
Spiritan University, Nneochi Abia State
Sports University, Idumuje, Ugboko, Delta State
Summit University, Offa
Tansian University, Umunya
The Duke Medical University, Calabar, Cross River State
Thomas Adewumi University, Oko-Irese, Kwara State
Topfaith University, Mkpatak, Akwa Ibom State
Trinity University, Ogun State
University of Mkar, Mkar
University of Offa, Kwara State
University on the Niger, Umunya, Anambra State
Venite University, Iloro-Ekiti, Ekiti State
Veritas University, Abuja
Vision University, Ikogbo, Ogun State
Wellspring University, Evbuobanosa – Edo State
Wesley University, Ondo
West Midlands Open University, Ibadan, Oyo State
Western Delta University, Oghara Delta State
Westland University, Iwo, Osun State
Wigwe University, Isiokpo Rivers State

Here is a formatted list of Canadian supported schools:
Brock University
Carleton University
Dalhousie University
Lakehead University
McMaster University
New York Institute of Technology (NYIT)
Northeastern University
Queens University at Kingston
Ryerson University
Trent University
Toronto Metropolitan University
University of Alberta
University of Calgary
University of Guelph
University of Lethbridge
University of Ottawa
University of Toronto
University of Victoria
University of Waterloo
University of Windsor
Western University – University of Western Ontario
Wilfrid Laurier University
York University
University of New Brunswick
University of Saskatchewan
University of Manitoba


"""

print(the_time)

active_conversations = {}

def send_whatsapp_message(data):
    recipient = data.get("recipient")
    text = data.get("text")
    sending_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    
    response = requests.post(url, json=sending_data, headers=headers)

    if response.status_code != 200:
        print("WhatsApp failed to send message!")
    return response

def verify_webhook_token(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        logging.info(f"Verification attempt - Mode: {mode}, Token: {token}, Challenge: {challenge}")
        logging.info(f"Stored VERIFY_TOKEN: {VERIFY_TOKEN}")
        print (VERIFY_TOKEN)

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logging.info("Verification successful")
            return HttpResponse(challenge, content_type="text/plain")
            response["Access-Control-Allow-Origin"] = "*"
            return response
        else:
            logging.warning("Verification failed")
            return JsonResponse({'error': 'Verification token mismatch'}, status=403)
    
    return JsonResponse({'method_not_allowed': True}, status=405)

def bot_respond(input_text, sender_id, recipient_id):
    try:
        response_text = bot_process(input_text, sender_id, recipient_id)
        return response_text
    except Exception as e:
        error_message = f"Error generating bot response: {e}"
        print(error_message)
        return f"Sorry, I couldn't generate a response at the moment. Error: {error_message}"

def is_valid_message(message):
    text_content = message.get('text', {}).get('body', '').lower()
    from_id = message.get('from')

    if len(text_content.split()) < 1:
        print(f'{len(text_content.split())} words long message')
        return False

    if from_id in active_conversations:
        last_activity = active_conversations[from_id]
        if datetime.now() - last_activity < timedelta(seconds=INACTIVITY_TIMEOUT):
            active_conversations[from_id] = datetime.now()
        else:
            del active_conversations[from_id]
            print('Inactive conversation')
            return False
    else:
        active_conversations[from_id] = datetime.now()
    return True

def save_inactive_conversations(request):
    current_time = time.time()
    saved_conversations = []  # List to store the phone numbers of saved conversations

    for from_id, last_activity_time in list(active_conversations.items()):
        sender_id = from_id
        recipient_id = from_id  # Assuming recipient_id is the same as from_id

        # Save chat history without checking inactivity timeout
        chat_history = cache.get(f'chat_history_{sender_id}_{recipient_id}', [])

        save_chat_history(sender_id, recipient_id, chat_history)

        # Add the phone number to the list of saved conversations
        saved_conversations.append(recipient_id)

        cache.delete(f'chat_history_{sender_id}_{recipient_id}')
        cache.delete(f'last_activity_{sender_id}_{recipient_id}')
        cache.delete(f'inactivity_message_sent_{sender_id}_{recipient_id}')

        del active_conversations[from_id]

    # Check if any conversations were saved
    if saved_conversations:
        # Construct the message with the phone numbers of saved conversations
        whatsapp_message = f'Convo auto saved: {", ".join(saved_conversations)}'
        sendingData = {
            "recipient": '255755888555',
            "text": whatsapp_message
        }
        print('=================================')
        print(whatsapp_message)
        print('=================================')
        send_whatsapp_message(sendingData)
    else:
        # If no conversations were saved, send a message indicating no activity
        sendingData = {
            "recipient": '255755888555',
            "text": 'No activity, no numbers were found in saved conversations'
        }
        print('=================================')
        print('No activity')
        print('=================================')
        send_whatsapp_message(sendingData)

# Schedule the next check
    # request.loop.call_later(CHECK_INTERVAL, save_inactive_conversations, request)


def bot_process(input_text, sender_id, recipient_id):
    user_input = input_text
    chat_history = cache.get(f'chat_history_{sender_id}_{recipient_id}', [])

    inactivity_message = (
        "You were inactive for a minute there.\n"
        "If you would like to continue with our last issue reply with '*YES*'.\n"
        "If you would like me to assist you with a new issue now, please reply with '*NEW*' or '*NEW ISSUE*'."
    )

    try:
        # Remove inactivity checks
        # last_activity = cache.get(f'last_activity_{sender_id}_{recipient_id}', time.time())
        # inactivity_message_sent = cache.get(f'inactivity_message_sent_{sender_id}_{recipient_id}', False)
        
        # Append user input to chat history
        chat_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=LLM_model,
            messages=[{"role": "system", "content": LLM_role_instructions}] + chat_history,
            max_tokens=256,
            temperature=0.5
        )

        assistant_response = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": assistant_response})

        # Save chat history after every interaction
        cache.set(f'chat_history_{sender_id}_{recipient_id}', chat_history, timeout=None)
        save_chat_history(sender_id, recipient_id, chat_history)

        return assistant_response

    except Exception as e:
        return f"Error generating bot response: {e}"



def continue_conversation(sender_id, recipient_id, chat_history):
    cache.set(f'chat_history_{sender_id}_{recipient_id}', chat_history, timeout=None)
    return "Great! Let's continue our conversation."

from django.db.models import F

def save_chat_history(sender_id, recipient_id, chat_history):
    chat_record, created = ChatHistory.objects.update_or_create(
        sender_id=sender_id,
        recipient_id=recipient_id,
        defaults={'chat_history': chat_history}
    )
    
    if created:
        message = f'New chat history created for: {recipient_id}'
    else:
        message = f'Chat history updated for: {recipient_id}'
    
    sendingData = {
        "recipient": '255755888555',
        "text": message
    }
    # send_whatsapp_message(sendingData)
    print(f'\n {message}')