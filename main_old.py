from typing import Union
from fastapi import FastAPI, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
app = FastAPI()

account_sid = 'ACfbd1aa720007424422c2870b148d689a'
auth_token = 'fa72a444251ed140ba0ac2d7451bd56d'
client = Client(account_sid, auth_token)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/message")
async def message_handler(req: Request):
    twilio_data = await req.form()

    message_body = twilio_data.get('Body','')

    response_message = "Received message: " + message_body
    
    senderNumber = twilio_data.get('From','')
    ProfileName = twilio_data.get('ProfileName', '')

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'Selamat datang, {ProfileName}! Ada yang dapat kami bantu?',
        to=senderNumber
        )

    twiml_response = MessagingResponse()
    twiml_response.message(response_message)

    return twiml_response.to_xml()
    
# def message_handler(item: dict):
    # print(f"Payload: {item}")
    # return item

