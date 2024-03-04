from typing import Union
from typing import List, Annotated

from fastapi import FastAPI, Request, HTTPException, Depends


# import SQLAlchemy from provider
import provider.models
from provider.db import engine, SessionLocal
from sqlalchemy.orm import Session
from provider.send_response import ResponseHandler

# create database column
provider.models.Base.metadata.create_all(bind=engine)
tw = ResponseHandler()

# activate database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()

# create fastapi endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/message")
def read_root():
    return {"Hello": "World"}

@app.post("/message")
async def message_handler(req: Request, db: db_dependency):

    incoming_payload = await req.json()

    # sumber
    message_body = incoming_payload.get('pesan','')
    print(message_body)
    nomor_hp = incoming_payload.get('pengirim', '')
    name = incoming_payload.get('name', 'User')

    response_message = "Received message: " + message_body

    # check user
    user_activity = db.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()
    
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
            return {"success": True}
            
        if user_activity.activity == 'decision':
            # change activity
            user_activity.activity = f'service_{message_body}'
            db.commit()

            # if else
            if message_body == "1":
                user_activity.activity = f'service_1'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilih jenis formulir yang dibutuhkan: \na. Formulir KTP\nb. Formulir Usaha\nc. Formulir Rekomendasi")                
                return {"success": True}

            if message_body == "2":
                user_activity.activity = f'service_2'
                db.commit()
                tw.sendMsg(nomor_hp, f"Sistem pembuatan laporan sedang dalam proses (ketik 'menu' untuk kembali)")
                return {"success": True}
            
            if message_body not in ['1','2']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan anda tidak ada.")                
            return {"success": True}
        
        # membuat form otomatis

        if user_activity.activity == 'service_1':
            print("masuk ke service")

            # lanjutin pembuatan form berdasarkan data yang diisi
            if message_body == 'a':
                user_activity.activity = f'service_1#KTP#nama'
                tw.sendMsg(nomor_hp, f"Beritahu kamu nama siapa nama anda?")
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
            return {"success": True}
        elif user_activity.activity.startswith('service_1#'):
            user_activity.activity.split('#')
            act = user_activity.activity.split('#')
            print(act)
            if act[1] == 'KTP':
                if act[2] == "nama":
                    # Insert first data to form_ktp
                    new_ktp_form = provider.models.form_ktp(nama=message_body, id_user_activity=int(user_activity.id))
                    db.add(new_ktp_form)
                    db.commit()
                    print(new_ktp_form.id_form_ktp)
                    # Update Activity
                    user_activity.activity = f'service_1#KTP#alamat#{new_ktp_form.id_form_ktp}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana anda tinggal?")             
                if act[2] == "alamat":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.alamat = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#nik#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa nama usaha anda?")   
                if act[2] == "nik":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.alamat = message_body
                    db.commit()
                    user_activity.activity = f'finish'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Berikut dokumen anda")            


            if act[1] == 'Rekomendasi':
                tw.sendMsg(nomor_hp, f"Berikut surat rekomendasi anda")                
            return {"success": True}

        # membuat laporan customer service
        if user_activity.activity.startswith('service_2'):
            user_activity.activity = f'service_report'
            db.commit()
            return {"success": True}

    return {"success": True}
    
# def message_handler(item: dict):
    # print(f"Payload: {item}")
    # return item

