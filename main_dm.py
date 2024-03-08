from typing import Union
from typing import List, Annotated

# FastAPI
from fastapi import FastAPI, Request, HTTPException, Depends

# import SQLAlchemy from provider
import provider.models
from provider.db import engine, SessionLocal
from sqlalchemy.orm import Session

# import PDFmaker
# from provider.pdf import autoPDF

# Fonnte Connection
from provider.send_rq import ResponseHandler
tw = ResponseHandler()


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

    user_activity = db.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()
    
    # cek aktivitas user & greeting
    if user_activity == 'None' or user_activity == None:
        tw.sendMsg(nomor_hp, f"Selamat datang dalam sistem KOPITU Desa AI, {name}! Ketik 'mulai' untuk menu pilihan.")
        new_user = provider.models.user_activity(no_hp=nomor_hp, activity='registered')
        db.add(new_user)
        db.commit()
    
    if user_activity.no_hp == nomor_hp:
        # membuat form otomatis
        if user_activity.activity == 'registered':
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
                tw.sendMsg(nomor_hp, f"Pilih jenis formulir yang dibutuhkan: \na. Formulir KTP\nb. Formulir Usaha\nc. Formulir Rekomendasi\nd. Surat Keterangan Tidak Mampu")                
                return {"success": True}

            if message_body == "2":
                # user_activity.activity = f'service_2'
                user_activity.activity = f'registrating'
                db.commit()
                tw.sendMsg(nomor_hp, f"Sistem pembuatan laporan sedang dalam proses (ketik 'menu' untuk kembali)")
                return {"success": True}
            
            if message_body not in ['1','2']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada.")                
            return {"success": True}
        
        # membuat form otomatis

        if user_activity.activity == 'service_1':
            print("masuk ke service")

            # lanjutin pembuatan form berdasarkan data yang diisi
            if message_body == 'a'|'A':
                user_activity.activity = f'service_1#KTP#nama'
                tw.sendMsg(nomor_hp, f"-=Proses pembuatan surat mengurus KTP=-\nSiapa nama Anda?")
                db.commit()                    
            if message_body == 'b'|'B':
                user_activity.activity = f'service_1#Usaha#Nama'
                tw.sendMsg(nomor_hp, f"-=Proses pembuatan surat mengurus Usaha=-\nSiapa nama Anda?")
                db.commit() 
            if message_body == 'c'|'C':
                user_activity.activity = f'service_1#Rekomendasi'
                tw.sendMsg(nomor_hp, f"-=Proses pembuatan surat mengurus Rekomendasi=-\nSiapa nama Anda?")
                db.commit()
            if message_body == 'd' | 'D':
                user_activity.activity = f'service_1#SKTM'
                tw.sendMsg(nomor_hp, f"-=Proses pembuatan surat mengurus Surat Keterangan Tidak Mampu (SKTM)=-\nSiapa nama Anda?")
                db.commit()             
            if message_body not in ['a','A','b','B','c','C','d','D']:
                user_activity.activity = 'registered'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada.\nKetik 'menu' untuk kembali.")
            return {"success": True}
        
        elif user_activity.activity.startswith('service_1#'):
            user_activity.activity.split('#')
            act = user_activity.activity.split('#')
            print(act)
            # FORM KTP
            if act[1] == 'KTP':
                if act[2] == 'nama':
                    # Insert first data to form_ktp
                    new_ktp_form = provider.models.form_ktp(nama=message_body, id_user_activity=int(user_activity.id))
                    db.add(new_ktp_form)
                    db.commit()
                    print(new_ktp_form.id_form_ktp)
                    # Update Activity
                    user_activity.activity = f'service_1#KTP#no_kk#{new_ktp_form.id_form_ktp}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa Nomor Kartu Keluarga Anda?")
                if act[2] == "no_kk":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.no_kk = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#nik#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa Nomor Induk Keluarga (NIK) Anda?")
                if act[2] == "nik":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.nik = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#alamat#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana alamat tempat tinggal Anda?")            
                if act[2] == "alamat":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.alamat = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#RTRW#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Kapan Anda lahir? (TANGGAL/BULAN/TAHUN contoh 19/10/1970 atau 19 Desember 1970)")
                if act[2] == "RTRW":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.rtrw = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#desa#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana desa Anda tinggal?")
                if act[2] == "desa":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.desa = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#kecamatan#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana kecamatan Anda tinggal?")
                if act[2] == "kecamatan":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.kecamatan = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#kabupaten_kota#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana Kabupaten/Kota Anda tinggal?")
                if act[2] == "kabupaten_kota":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.kabupaten_kota = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#desa#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana Provinsi Anda tinggal?")
                if act[2] == "provinsi":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.provinsi = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#tujuan_surat#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa tujuan pembuatan surat Anda? (PEMBUATAN KTP BARU/PEMBAHARUAN/KEHILANGAN)")
                if act[2] == "tujuan_surat":
                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_form_ktp = act[3]).first()
                    existing_ktp_form.tujuan_surat = message_body
                    db.commit()
                    user_activity.activity = f'service_1#KTP#finish#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")

            ## FORM USAHA
            if act[1] == 'Usaha':
                if act[2] == "nama":
                    # Insert first data to form_usaha
                    new_usaha_form = provider.models.form_usaha(nama=message_body, id_user_activity=int(user_activity.id))
                    db.add(new_usaha_form)
                    db.commit()
                    print(new_usaha_form.id_form_usaha)
                    # Update Activity
                    user_activity.activity = f'service_1#Usaha#nik#{new_usaha_form.id_form_usaha}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa NIK (Nomor Induk Keluarga) Anda?")
                if act[2] == "nik":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.nik = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#jenis_kelamin#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa jenis kelamin Anda? (P/L)")
                if act[2] == "jenis_kelamin":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.jenis_kelamin = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#ttl#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Kapan Anda lahir? (TANGGAL/BULAN/TAHUN contoh 19/10/1970)")            
                if act[2] == "ttl":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.ttl = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#alamat#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana tempat tinggal Anda?")            
                if act[2] == "alamat":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.alamat = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#pekerjaan#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa pekerjaan Anda saat ini?")            
                if act[2] == "pekerjaan":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.pekerjaan = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#RTRW#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"RT/RW rumah Anda? (contoh 01/03)")            
                if act[2] == "RTRW":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.rtrw = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#nama_usaha#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa nama usaha Anda?")            
                if act[2] == "nama_usaha":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.nama_usaha = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#start_usaha#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Kapan usaha dimulai?")            
                if act[2] == "start_usaha":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.start_usaha = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#alamat_usaha#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Dimana alamat usaha Anda?")            
                if act[2] == "alamat_usaha":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.alamat_usaha = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#tujuan_surat#{act[3]}'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Apa tujuan pembuatan surat anda? (Tulis selengkapnya)")            
                if act[2] == "tujuan_surat":
                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_form_usaha = act[3]).first()
                    existing_usaha_form.tujuan_surat = message_body
                    db.commit()
                    user_activity.activity = f'service_1#Usaha#finish#{act[3]}'
                    # user_activity.activity = f'registered'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")                      

            if act[1] == 'Rekomendasi':
                tw.sendMsg(nomor_hp, f"Berikut surat rekomendasi Anda")                
            return {"success": True}

        # membuat laporan customer service
        if user_activity.activity.startswith('service_2'):
            # user_activity.activity = f'service_report'
            user_activity.activity = f'registered'
            db.commit()
            tw.sendMsg(nomor_hp, f"Layanan sedang dalam proses perbaikan. Coba lagi nanti.\n(Ketik 'menu' untuk kembali.)")            
            return {"success": True}

    return {"success": True}
    
# def message_handler(item: dict):
    # print(f"Payload: {item}")
    # return item

