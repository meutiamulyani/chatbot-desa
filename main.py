from typing import Union
from typing import List, Annotated

# FastAPI
from fastapi import FastAPI, Request, HTTPException, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import requests

# import SQLAlchemy from provider
import provider.models
from provider.db import engine, SessionLocal
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import update

# import function
from function.docxauto import Doc_Auto

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

# activate FastAPI
db_dependency = Annotated[Session, Depends(get_db)]
Session = sessionmaker(bind=engine)
word = Doc_Auto(db_con=Session(), model=provider.models)
app = FastAPI()

# Create a directory to store uploaded files
UPLOAD_DIRECTORY = "public"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Mount the public directory to serve static files
app.mount("/files", StaticFiles(directory=UPLOAD_DIRECTORY), name="files")

# ==================================================
# FastAPI endpoints
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/message")
def read_root():
    return {"Hello": "World"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    payload = await Request.json()
    nomor_hp = payload.get('pengirim', '')

    # Generate file name based on ID/phone number
    user_id = db_dependency.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()
    file_extension = os.path.splitext(file.filename)[-1]
    file_name = f"doc_{user_id.no_hp}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
    
    # Write the uploaded file to the public directory
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Construct the URL of the uploaded file
    file_url = f"/files/{file_name}"
    
    return {"file_path": file_path, "file_url": file_url}

@app.post("/message")
async def message_handler(req: Request, db: db_dependency):
    incoming_payload = await req.json()
    
    # sumber
    message_body = incoming_payload.get('pesan','')
    print(message_body)
    nomor_hp = incoming_payload.get('pengirim', '')
    name = incoming_payload.get('name', 'User')

    # response_message = "Received message: " + message_body

    user_activity = db.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()
    print(provider.models.user_activity)
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
            tw.sendMsg(nomor_hp, f"Apa yang dapat kami bantu?\n1. Membuat Formulir Administrasi\n2. Membuat Laporan")
            return {"success": True}
        
        if user_activity.activity == 'decision':
            # change activity
            user_activity.activity = f'service_{message_body}'
            db.commit()

            # if else based on choice
            if message_body == "1":
                user_activity.activity = f'service_1'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilih jenis formulir yang dibutuhkan: \na. Formulir KTP\nb. Formulir Usaha\nc. Formulir Rekomendasi\nd. Surat Keterangan Tidak Mampu")                
                return {"success": True}

            if message_body == "2":
                # user_activity.activity = f'service_2'
                user_activity.activity = f'registered'
                db.commit()
                tw.sendMsg(nomor_hp, f"Sistem pembuatan laporan sedang dalam proses (ketik 'menu' untuk kembali ke pilihan awal.)")
                return {"success": True}
            
            if message_body == "3":
                # user_activity.activity = f'service_2'
                user_activity.activity = f'registered'
                db.commit()
                tw.sendMsg(nomor_hp, f"Sistem FAQ sedang dalam proses (ketik 'menu' untuk kembali ke pilihan awal.)")
                return {"success": True}      
                
            if message_body not in ['1','2','3']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada.")                
            return {"success": True}
        
        # membuat form otomatis

        if user_activity.activity == 'service_1':
            # lanjutin pembuatan form berdasarkan data yang diisi
            if message_body == 'a' or 'A':
                user_activity.activity = f'service_1#KTP#fill'
                tw.sendMsg(nomor_hp, f"""-=Proses pembuatan surat mengurus KTP=-\nIsilah data berikut dengan lengkap:\n1. Nama lengkap\n2. No.Kartu Keluarga\n3. Nomor Induk Kependudukan (NIK)\n4. Alamat Tempat Tinggal\n5. RT/RW\n6. Desa\n7. Kecamatan\n8. Kabupaten/Kota\n9. Provinsi\n10. Tujuan Surat(Pembuatan/Pembaharuan/Laporan Kehilangan)\nBalas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, 10 desember 1990, dll)""")
                db.commit()

            elif message_body == 'b' or 'B':
                user_activity.activity = f'service_1#Usaha#fill'
                tw.sendMsg(nomor_hp, f"""-=Proses pembuatan surat mengurus Usaha=-\nIsilah data berikut dengan lengkap:
                           1. Nama lengkap\n2. Nomor Induk Kependudukan (NIK)\n3. Jenis Kelamin (P/L)
                           4. Tempat/Tanggal Lahir\n5.Alamat Tempat Tinggal\n6. RT/RW\n7. Pekerjaan\n8. Nama Usaha\n
                           9. Tanggal Usaha Dimulai\n10. Tujuan Surat
                           Balas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, 10 desember 1990, dll)""")
                db.commit()

            elif message_body == 'c' or 'C':
                user_activity.activity = f'service_1#Rekomendasi#fill'
                tw.sendMsg(nomor_hp, f"""-=Proses pembuatan surat mengurus Usaha=-\nIsilah data berikut dengan lengkap:\n1. Nama lengkap\n2. Nomor Induk Kependudukan (NIK)\n3. Tempat/Tanggal Lahir\n4. Warganegara\n7. Agama\n8. Pekerjaan\n9. Alamat\n10. Tujuan Surat Rekomendasi\nBalas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, 10 desember 1990, dll)""")
                db.commit()

            elif message_body == 'd' or 'D':
                user_activity.activity = f'service_1#SKTM#fill'
                tw.sendMsg(nomor_hp, f"-=Proses pembuatan surat mengurus Surat Keterangan Tidak Mampu (SKTM)=-\n(sedang dalam proses)")
                db.commit()
                      
            elif message_body not in ['a','A','b','B','c','C','d','D']:
                user_activity.activity = 'registered'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada.\nKetik 'menu' untuk kembali.")
            return {"success": True}
        
        if user_activity.activity.startswith('service_1#'):
            user_activity.activity.split('#')
            act = user_activity.activity.split('#')
            # FORM KTP
            if act[1] == 'KTP':
                text = message_body
                data_text = text.split(',')
                ## buat if else seandainya datanya udah ada.
                if len(data_text) == 10:
                    item = provider.models.form_ktp(
                        nama=data_text[0],
                        no_kk=data_text[1],
                        nik=data_text[2],
                        alamat=data_text[3],
                        rtrw=data_text[4],
                        desa=data_text[5],
                        kecamatan=data_text[6],
                        kabupaten_kota=data_text[7],
                        provinsi=data_text[8],
                        tujuan_surat=data_text[9],
                        id_user_activity=int(user_activity.id))

                    existing_ktp_form = db.query(provider.models.form_ktp).filter_by(id_user_activity = user_activity.id).first()
                    if existing_ktp_form:
                        existing_ktp_form.nama = item.nama
                        existing_ktp_form.no_kk = item.no_kk
                        existing_ktp_form.nik = item.nik
                        existing_ktp_form.alamat = item.alamat
                        existing_ktp_form.rtrw = item.rtrw
                        existing_ktp_form.desa = item.desa
                        existing_ktp_form.kecamatan = item.kecamatan
                        existing_ktp_form.kabupaten_kota = item.kabupaten_kota
                        existing_ktp_form.provinsi = item.provinsi
                        existing_ktp_form.tujuan_surat = item.tujuan_surat  
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'KTP') # <- buat status pembuatan form
                        user_activity.activity = f'finish'
                        db.commit()

                        # Doc_Auto.doc_ktp(user_activity)
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")
                    else:
                        db.add(item)
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'KTP') #<- buat status pembuatan form
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")

                if len(data_text) < 10:
                    user_activity.activity = f'service_1#KTP#fill'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")
                
                if len(data_text) > 10:
                    user_activity.activity = f'service_1#KTP#fill'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")

            if act[1] == 'Usaha':
                text = message_body
                data_text = text.split(',')
                ## buat if else seandainya datanya udah ada.
                if len(data_text) == 11:
                    item = provider.models.form_usaha(
                        nama=data_text[0],
                        nik=data_text[1],
                        jenis_kelamin=data_text[2],
                        ttl=data_text[3],
                        alamat=data_text[4],
                        pekerjaan=data_text[5],
                        rtrw=data_text[6],
                        nama_usaha=data_text[7],
                        start_usaha=data_text[8],
                        alamat_usaha=data_text[9],
                        tujuan_surat=data_text[10],
                        id_user_activity=int(user_activity.id))

                    existing_usaha_form = db.query(provider.models.form_usaha).filter_by(id_user_activity = user_activity.id).first()
                    if existing_usaha_form:
                        existing_usaha_form.nama = item.nama
                        existing_usaha_form.nik = item.nik
                        existing_usaha_form.jenis_kelamin = item.jenis_kelamin
                        existing_usaha_form.ttl = item.ttl
                        existing_usaha_form.alamat = item.alamat
                        existing_usaha_form.pekerjaan = item.pekerjaan
                        existing_usaha_form.rtrw = item.rtrw
                        existing_usaha_form.nama_usaha = item.nama_usaha
                        existing_usaha_form.start_usaha = item.start_usaha
                        existing_usaha_form.alamat_usaha = item.alamat_usaha
                        existing_usaha_form.tujuan_surat = item.tujuan_surat  
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'Usaha') # <- buat status pembuatan form
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")
                    else:
                        db.add(item)
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'Usaha') # <- buat status pembuatan form
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")

                if len(data_text) < 11:
                    user_activity.activity = f'service_1#'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if len(data_text) > 11:
                    user_activity.activity = f'service_1#'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")
            
            ## FORM USAHA
            if act[1] == 'Rekomendasi':
                text = message_body
                data_text = text.split(',')
                ## buat if else seandainya datanya udah ada.
                if len(data_text) == 8:
                    item = provider.models.form_rekomendasi(
                        nama=data_text[0],
                        nik=data_text[1],
                        ttl=data_text[2],
                        warganegara=data_text[3],
                        agama=data_text[4],
                        pekerjaan=data_text[5],
                        alamat=data_text[6],
                        tujuan_surat=data_text[7],
                        id_user_activity=int(user_activity.id))

                    existing_rekomendasi_form = db.query(provider.models.form_rekomendasi).filter_by(id_user_activity = user_activity.id).first()
                    if existing_rekomendasi_form:
                        existing_rekomendasi_form.nama = item.nama
                        existing_rekomendasi_form.nik = item.nik
                        existing_rekomendasi_form.ttl = item.ttl
                        existing_rekomendasi_form.warganegara = item.warganegara
                        existing_rekomendasi_form.agama = item.agama
                        existing_rekomendasi_form.pekerjaan = item.pekerjaan
                        existing_rekomendasi_form.alamat = item.alamat
                        existing_rekomendasi_form.tujuan_surat = item.tujuan_surat
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'Rekomendasi') # <- buat status pembuatan form  
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")
                    else:
                        db.add(item)
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'Rekomendasi') # <- buat status pembuatan form
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")

                if len(data_text) < 8:
                    user_activity.activity = f'service_1#'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if len(data_text) > 8:
                    user_activity.activity = f'service_1#'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")

            if act[1] == 'SKTM':
                text = message_body
                data_text = text.split(',')
                ## buat if else seandainya datanya udah ada.
                if len(data_text) == 10:
                    item = provider.models.form_sktm(
                        nama=data_text[0],
                        nik=data_text[1],
                        jenis_kelamin=data_text[2],
                        ttl=data_text[3],
                        warganegara=data_text[4],
                        agama=data_text[5],
                        pekerjaan=data_text[6],
                        status=data_text[7],
                        alamat=data_text[8],
                        tujuan_surat=data_text[9],
                        id_user_activity=int(user_activity.id))
                    existing_sktm_form = db.query(provider.models.form_sktm).filter_by(id_user_activity = user_activity.id).first()
                    if existing_sktm_form:
                        existing_sktm_form.nama = item.nama
                        existing_sktm_form.nik = item.nik
                        existing_sktm_form.jenis_kelamin = item.jenis_kelamin
                        existing_sktm_form.ttl = item.ttl
                        existing_sktm_form.warganegara = item.warganegara
                        existing_sktm_form.agama = item.agama
                        existing_sktm_form.pekerjaan = item.pekerjaan
                        existing_sktm_form.status = item.status
                        existing_sktm_form.alamat = item.alamat
                        existing_sktm_form.tujuan_surat = item.tujuan_surat
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'SKTM') # <- buat status pembuatan form  
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")
                    else:
                        db.add(item)
                        db.commit()
                        word.wrapper_doc(user_activity.no_hp, 'SKTM') # <- buat status pembuatan form
                        user_activity.activity = f'finish'
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n(Akun ujicoba gratis dan belum dapat mengirimkan attachment)\n\nKetik 'menu' untuk kembali.")

                if len(data_text) < 10:
                    user_activity.activity = f'service_1#'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if len(data_text) > 10:
                    user_activity.activity = f'service_1#'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")
            return {"success": True}

        # membuat laporan customer service
        if user_activity.activity.startswith('service_2'):
            # user_activity.activity = f'service_report'
            user_activity.activity = f'registered'
            db.commit()
            tw.sendMsg(nomor_hp, f"Layanan sedang dalam proses perbaikan. Coba lagi nanti.\n(Ketik 'mulai' untuk kembali.)")            
            return {"success": True}

        if user_activity.activity.startswith('service_3'):
            user_activity.activity = f'registered'
            db.commit()
            tw.sendMsg(nomor_hp, f"Layanan sedang dalam proses perbaikan. Coba lagi nanti.\n(Ketik 'mulai' untuk kembali.)")            
            return {"success": True}

        if user_activity.activity == 'finish':
            user_activity.activity = 'decision'
            db.commit()
            tw.sendMsg(nomor_hp, f"Apa yang dapat kami bantu?\n1. Membuat Formulir Administrasi\n2. Membuat Laporan\n")
            return {"success": True}
    return {"success": True}
    

