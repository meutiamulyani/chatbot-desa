from typing import Union
from typing import List, Annotated

from fastapi import FastAPI, Request, HTTPException, Depends

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# import SQLAlchemy from provider
import provider.models
from provider.db import engine, SessionLocal
from sqlalchemy.orm import Session

# twilio connection
from provider.send_twilio import TwilioNewConnection, TwilioHandler
tw = TwilioHandler()

# create database column
provider.models.Base.metadata.create_all(bind=engine)

# activate database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()
client = TwilioNewConnection()

# create fastapi endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/message")
async def message_handler(req: Request, db: db_dependency):

    twilio_data = await req.form()

    # sumber
    message_body = twilio_data.get('Body','')
    nomor_hp = twilio_data.get('From', '')
    print(nomor_hp)
    name = twilio_data.get('ProfileName', 'User')

    print(message_body)
    # print(twilio_data)
    response_message = "Received message: " + message_body

    # check user
    user_activity = db.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()
    # print(user_activity.no_hp)
    
    twiml_response = MessagingResponse()
    twiml_response.message(response_message)
    
    # cek aktivitas user & greeting
    if user_activity == 'None' or user_activity == None:
        tw.sendMsg(nomor_hp, f"Selamat datang {name}! Ketik 'mulai' untuk menu pilihan.")
        new_user = provider.models.user_activity(no_hp=nomor_hp, activity='registering')
        db.add(new_user)
        db.commit()
    
    if user_activity.no_hp == nomor_hp:
        # membuat form otomatis
        if user_activity.activity == 'registering':
            user_activity.activity = 'decision'
            db.commit()
            tw.sendMsg(nomor_hp, f"Apa yang dapat kami bantu?\n1. Membuat Formulir\n2. Membuat Laporan")
            return twiml_response.to_xml()
            
        if user_activity.activity == 'decision':
            # change activity
            user_activity.activity = f'service_{message_body}'
            db.commit()

            # if else
            if message_body == "1":
                user_activity.activity = f'service_1'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilih jenis formulir yang dibutuhkan: \na. Formulir KTP\nb. Formulir Usaha\nc. Formulir Rekomendasi")                
                return twiml_response.to_xml()

            if message_body == "2":
                user_activity.activity = f'service_2'
                db.commit()
                tw.sendMsg(nomor_hp, f"Sistem pembuatan laporan sedang dalam proses (ketik 'menu' untuk kembali)")
                return twiml_response.to_xml()
            
            if message_body not in ['1','2']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan anda tidak ada.")                
            return twiml_response.to_xml()
        
        # membuat form otomatis
        print("CURR ACT: ", user_activity.activity)
        print("SPLIT: ", user_activity.activity.split(","))
        if user_activity.activity == 'service_1':
            print("masuk ke service")

            # lanjutin pembuatan form berdasarkan data yang diisi
            if message_body == 'a':
                user_activity.activity = f'service_1#KTP'
                db.commit()                    
            if message_body == 'b':
                user_activity.activity = f'service_1#Usaha'
                db.commit() 
            if message_body == 'c':
                user_activity.activity = f'service_1#Rekomendasi'
                db.commit() 
            if message_body not in ['a','b','c']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan anda tidak ada.")
            return twiml_response.to_xml()
        elif user_activity.activity.startswith('service_1#'):
            user_activity.activity.split('#')
            act = user_activity.activity.split('#')
            print("masuk ke starswith")
            if act[1] == 'Rekomendasi':
                tw.sendMsg(nomor_hp, f"Berikut surat rekomendasi anda")                
            return twiml_response.to_xml()

        # membuat laporan customer service
        if user_activity.activity.startswith('service_2'):
            user_activity.activity = f'service_report'
            db.commit()
            return twiml_response.to_xml()

    return twiml_response.to_xml()
    
# def message_handler(item: dict):
    # print(f"Payload: {item}")
    # return item

