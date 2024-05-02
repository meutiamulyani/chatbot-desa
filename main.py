from typing import Union
from typing import List, Annotated
import threading, time
from dotenv import dotenv_values

# FastAPI
from fastapi import FastAPI, Request, HTTPException, Depends, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os, asyncio

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

@app.get("/download/{file_name}")
async def get_pdf(file_name: str, request: Request):
    client_host = request.client.host
    docx_path = f"public/files/{file_name}"

    if not os.path.exists(docx_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(docx_path, media_type="application/docx")

@app.post("/message")
async def message_handler(req: Request, db: db_dependency):
    incoming_payload = await req.json()
    protocol = req.url.scheme
    host = req.headers["host"]

    # DATA SOURCE
    message_body = incoming_payload.get('pesan','')
    print(message_body)
    nomor_hp = incoming_payload.get('pengirim', '')
    hp_admin = '6285324075075'
    name = incoming_payload.get('name', 'User')

    env_vars = dotenv_values(".env")
    admin_acc = env_vars.get('admin')

    # response_message = "Received message: " + message_body
    user_activity = db.query(provider.models.user_activity).filter_by(no_hp = nomor_hp).first()

    # cek aktivitas user & greeting
    if user_activity == 'None' or user_activity == None:
        tw.sendMsg(nomor_hp, f"Selamat datang dalam sistem Chatbot Desa Dompyong Kulon, {name}! Ketik 'mulai' untuk menu pilihan.")
        new_user = provider.models.user_activity(no_hp=nomor_hp, activity='registered')
        db.add(new_user)
        db.commit()
    
    # USER INTERFACE
    if user_activity.no_hp == nomor_hp:
        menu = "_(Kirim 'menu' untuk kembali ke pilihan awal.)_"
        # membuat form otomatis
        if user_activity.activity == 'registered':
            user_activity.activity = 'decision'
            db.commit()
            tw.sendMsg(nomor_hp, f"*[MENU UTAMA CHATBOT DESA DOMPYONG KULON]*\nApa yang dapat kami bantu, {name}?\n1. Membuat Formulir Administrasi Desa Dompyong Kulon\n2. Chat dengan Customer Service\n3. Informasi Umum")
            return {"success": True}
        
        if user_activity.activity == 'decision':
            # change activity
            user_activity.activity = f'service_{message_body}'
            db.commit()
            # if else based on choice
            if message_body == "1":
                user_activity.activity = f'service_1'
                db.commit()
                tw.sendMsg(nomor_hp, f"*[PEMBUATAN FORMULIR OTOMATIS]*\nPilih jenis formulir yang Anda butuhkan: \na. Formulir KTP\nb. Formulir Usaha\nc. Formulir Rekomendasi\nd. Surat Keterangan Tidak Mampu\n\n{menu}")                
                return {"success": True}

            if message_body == "2":
                user_activity.activity = f'service_2#cs#start'
                db.commit()
                tw.sendMsg(nomor_hp, f"*[LAYANAN CUSTOMER SERVICE]*\nApa laporan atau pertanyaan yang akan Anda ajukan?\n\n{menu}")                
                return {"success": True}
            
            if message_body == "3":
                user_activity.activity = f'service_3'
                db.commit()
                tw.sendMsg(nomor_hp, f"*[INFORMASI DESA DOMPYONG KULON]*\nApa informasi yang ingin Anda ketahui?\na. Tentang Desa Dompyong Kulon\nb. Tentang Sistem\n\n{menu}")
                return {"success": True}      
                
            if message_body not in ['1','2','3','menu','batal']:
                user_activity.activity = 'decision'
                db.commit()
                tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada. Silakan kirim kembali berdasarkan opsi yang disediakan.")                
                return {"success": True}

        # membuat form otomatis
        if user_activity.activity == 'service_1':
            # lanjutin pembuatan form berdasarkan data yang diisi
            # Form KTP
            if message_body == 'a' or message_body == 'A':
                user_activity.activity = f'service_1#KTP#fill'
                tw.sendMsg(nomor_hp, f"*[PROSES PEMBUATAN SURAT KTP]*=-\nIsilah data berikut dengan lengkap:\n1. Nama lengkap\n2. No.Kartu Keluarga\n3. Nomor Induk Kependudukan (NIK)\n4. Alamat Tempat Tinggal\n5. RT/RW\n6. Desa\n7. Kecamatan\n8. Kabupaten/Kota\n9. Provinsi\n10. Tujuan Surat(Pembuatan/Pembaharuan/Laporan Kehilangan)\nBalas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, surabaya/10 desember 1990, dst)")
                db.commit()
                return {"success": True}

            # Form KTP
            if message_body == 'b' or message_body =='B':
                user_activity.activity = f'service_1#Usaha#fill'
                tw.sendMsg(nomor_hp, f"""*[PROSES PEMBUATAN SURAT KETERANGAN USAHA]*\nIsilah data berikut dengan lengkap:\n1. Nama lengkap\n2. Nomor Induk Kependudukan (NIK)\n3. Jenis Kelamin (P/L)\n4. Tempat/Tanggal Lahir\n5.Alamat Tempat Tinggal\n6. RT/RW\n7. Pekerjaan\n8. Nama Usaha\n9. Tanggal Usaha Dimulai\n10. Alamat Usaha\n11. Tujuan Surat\n\nBalas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, 10 desember 1990, dst)""")
                db.commit()
                return {"success": True}

            # Form Rekomendasi
            if message_body == 'c' or message_body == 'C':
                user_activity.activity = f'service_1#Rekomendasi#fill'
                tw.sendMsg(nomor_hp, f"""[PROSES PEMBUATAN SURAT REKOMENDASI]\nIsilah data berikut dengan lengkap:\n1. Nama lengkap\n2. Nomor Induk Kependudukan (NIK)\n3. Tempat/Tanggal Lahir\n4. Warganegara\n7. Agama\n8. Pekerjaan\n9. Alamat\n10. Tujuan Surat Rekomendasi\nBalas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, 10 desember 1990, dst)""")
                db.commit()
                return {"success": True}

            # Form SKTM
            if message_body == 'd' or message_body == 'D':
                user_activity.activity = f'service_1#SKTM#fill'
                tw.sendMsg(nomor_hp, f"[PROSES PEMBBUATAN SURAT KETERANGAN TIDAK MAMPU (SKTM)]\nIsilah data berikut dengan lengkap:\n1. Nama lengkap\n2. Nomor Induk Kependudukan (NIK)\n3. Jenis Kelamin (P/L)\n4. Tempat/Tanggal Lahir\n5. Warga Negara\n6. Agama\n7. Pekerjaan\n8. Status\n9. Alamat Lengkap\n10. Tujuan Surat\nBalas dalam satu pesan hingga seluruh data lengkap\n(Contoh: desti, 123456789, 10 desember 1990, dst)")
                db.commit()
                return {"success": True}

            if message_body not in ['a','b','c','A','B','C','menu']:
                tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada. Silakan kirim kembali berdasarkan opsi yang disediakan.")
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
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'KTP') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        # Doc_Auto.doc_ktp(user_activity)
                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_ktp_form.nama}")
                        return {"success": True}
                    else:
                        db.add(item)
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'KTP') #<- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_ktp_form.nama}")
                        return {"success": True}


                elif len(data_text) < 10 and message_body not in ['menu']:
                    user_activity.activity = f'service_1#KTP#fill'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")
                    return {"success": True}
                
                elif len(data_text) > 10:
                    user_activity.activity = f'service_1#KTP#fill'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")
                    return {"success": True}

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

                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'Usaha') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_usaha_form.nama}")
                        return {"success": True}

                    else:
                        db.add(item)
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'Usaha') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_usaha_form.nama}")
                        return {"success": True}

                if len(data_text) < 11:
                    user_activity.activity = f'service_1#Usaha#fill'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")
                    return {"success": True}

                if len(data_text) > 11:
                    user_activity.activity = f'service_1#Usaha#fill'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")
                    return {"success": True}
              
            ## FORM REKOMENDASI
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
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'Rekomendasi') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_rekomendasi_form.nama}")
                        return {"success": True}

                    else:
                        db.add(item)
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'Rekomendasi') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_rekomendasi_form.nama}")
                        return {"success": True}

                if len(data_text) < 8:
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if len(data_text) > 8:
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if message_body == 'batal' or message_body == 'Batal':
                    user_activity.activity = 'decision'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Selamat datang kembali!\nApa yang dapat kami bantu, {name}?\n1. Membuat Formulir Administrasi Desa Dompyong Kulon\n2. Chat dengan Customer Service\n3. Informasi Umum")
                    return {"success": True}
                
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
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'SKTM') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_sktm_form.nama}")
                        return {"success": True}

                    else:
                        db.add(item)
                        db.commit()
                        tw.sendMsg(nomor_hp, f"Dokumen sedang diproses, mohon ditunggu. Pengolahan dokumen dapat memakan waktu 1 hingga 5 menit")
                        file_name = word.wrapper_doc(user_activity.no_hp, 'SKTM') # <- buat status pembuatan form
                        url = f'{protocol}://{host}/download/{file_name}.docx'
                        user_activity.activity = f'finish'
                        db.commit()

                        tw.sendAttach(nomor_hp, url, f"Terima kasih. Berikut dokumen anda yang telah diproses.\n\nLink bila dokumen tidak dapat dibuka: {url}\n\nKetik 'menu' untuk kembali.")
                        tw.sendAdmin(hp_admin, url, f"Berikut data yang dikirimkan oleh {existing_sktm_form.nama}")
                        return {"success": True}


                if len(data_text) < 10:
                    tw.sendMsg(nomor_hp, f"Data kurang/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if len(data_text) > 10:
                    tw.sendMsg(nomor_hp, f"Data yang diberikan terlalu banyak/tidak memenuhi format pengiriman. Silakan coba lagi.")

                if message_body == 'batal' or message_body == 'Batal':
                    user_activity.activity = 'decision'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Selamat datang kembali!\nApa yang dapat kami bantu, {name}?\n1. Membuat Formulir Administrasi Desa Dompyong Kulon\n2. Chat dengan Customer Service\n3. Informasi Umum")
                    return {"success": True}
            return {"success": True}

        # Chat dengan Customer Service customer service
        if user_activity.activity.startswith('service_2'):
            # def timeout(event):
            #     global message_body
            #     if message_body is None and not event.is_set():
            #         user_activity.activity = f'finish'
            #         db.commit()
            #         tw.sendMsg(nomor_hp, f"*[CUSTOMER SERVICE]* layanan customer service sedang di luar jangkauan. Harap coba lagi nanti.")            

            act_cs = user_activity.activity.split('#')
            # TUNGGU RESPON AGENTS
            if act_cs[2] == 'start':
                tw.sendMsg(nomor_hp, f"*[CUSTOMER SERVICE]*\nSebentar lagi admin akan berkomunikasi dengan Anda, harap menunggu sebentar. (pilih 'finish' atau 'end' untuk mengakhiri sesi percakapan.)")            
                user_activity.activity = 'service_2#cs#incommunication'
                db.commit()
                # event = threading.Event()
                # # Start the timer thread
                # timer = threading.Timer(10, timeout, args=(event,))
                # timer.start()
                
                # while True:
                #     # Simulate receiving message body from WhatsApp (replace with your actual logic)
                #     # For demonstration, we'll just set a message body every 10 seconds
                #     print("Received message:", message_body)

                #     # Set the event flag to indicate that a message was received
                #     event.set()

                #     # Reset the event flag for the next iteration
                #     event.clear()

                #     # Sleep for 10 seconds (simulating a delay between messages)
                #     time.sleep(10)

            if act_cs[2] == 'incommunication':                                    
                if message_body == 'finish' or message_body == 'end':
                    user_activity.activity = f'finish'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"sesi percakapan telah berakhir, terima kasih telah menghubungi administrator kami. {menu}")
                    # event.clear()
                            
            return {"success": True}

        # FAQ Desa Dompyong Kulon
        if user_activity.activity == 'service_3':
            if message_body == 'a':
                tw.sendMsg(nomor_hp, f"*[INFORMASI DESA DOMPYONG KULON]*\nApa yang ingin Anda ketahui tentang Desa Dompyong Kulon?\n1. Tentang Desa\n2. Susunan Organisasi dan Tata Kerja (SOTK)\n3. Sejarah Singkat Desa\n4. Sarana dan Pra sarana Desa\n5. Program Desa")            
                user_activity.activity = 'service_3#faq#desa'
                db.commit()
                return {"success": True}                              
            elif message_body == 'b':
                tw.sendMsg(nomor_hp, f"*[INFORMASI DESA DOMPYONG KULON]*\n1. Tentang chatbot\n2. Fitur saat ini\n3. Cara membuat dokumen lewat chatbot")
                user_activity.activity = f'service_3#faq#sistem'
                db.commit()
                return {"success": True}                              
            elif message_body not in ['a', 'b', 'kembali', 'menu']:
                tw.sendMsg(nomor_hp, 'Pilihan ada tidak ada, silakan membalas "kembali" atau pilih "menu" untuk kembali ke menu.')
                return {"success": True}

        if user_activity.activity.startswith('service_3#'):
            act_faq = user_activity.activity.split('#')
            back = '_(Pilih "kembali" untuk melihat informasi lain atau "menu" untuk kembali ke menu.)_'
            if act_faq[2] == 'desa':
                # TENTANG DESA
                if message_body == '1' or message_body.startswith('tentang'):
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*[TENTANG DESA DOMPYONG KULON]*\n\nDesa Dompyong Kulon adalah salah satu desa di Kecamatan Gebang yang mempunyai luas wilayah 234,47 Ha , 136 Ha Tanah Pertanian,30,47 Ha dan 68 Ha Perumahan Tanah Bubulak dan Jumlah penduduk  sebanyak 4.343  jiwa yang terdiri dari 2.119 laki-laki dan 2.096 perempuan dengan jumlah Kepala Keluarga sebanyak 1461 KK. Sedangkan jumlah Keluarga Miskin (Gakin) 1201 KK dengan prosentasi 10 % dari jumlah keluarga yang ada di  Kec. Gebang\n\nBatas-batas administratif pemerintah  Kecamatan Gebang sebagai berikut :\n- Sebelah Utara	:	Desa Kalimaro Kec. Gebang\n- Sebelah Timur	:	Desa Dompyongwetan Kec. Gebang\n- Sebelah Selatan	:	Desa Genbongan Mekar Kec. Babakan\n- Sebelah Barat	:	Desa Getrakmoyan Kec. Pangenan\n\nDilihat dari topografi dan kontur tanah,  Kecamatan Gebang secara umum berupa Dataran yang berada pada ketinggian antara 1  s/d  1,5m di atas permukaan air laut. Dengan suhu rata-rata berkisar antara 28 s/d 32.° C.  terdiri dari 4 (Empat) Dusun, 4 (Enam) RW dan 16 (Enam Belas) RT. Orbitasi dan  jarak tempuh dari ibu kota kecamatan 3 km dengan  waktu tempuh 15 menit dengan menggunakan sepeda motor,dan dari ibu kota kabupaten 45 km, dengan waktu tempuh ± 60  menit dengan menggunakan sepeda motor.\n\n{back}")
                    return {"success": True}

                # TENTANG ORGANISASI DESA
                if message_body == '2' or message_body.startswith('organisasi'):
                    user_activity.activity = 'service_3#faq#org'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*STRUKTUR ORGANISASI DESA*\n\nPilih jenis struktur organisasi yang dibutuhkan:\na. Susunan Organisasi dan Tata Kerja (SOTK)\nb. Badan Permusyawaratan Desa (BPD)\nc. Lembaga Pemberdayaan Masyarakat Desa (LPMD)\n\n{back}")
                    return {"success": True}                              
                # SEJARAH DESA
                if message_body == '3' or message_body.startswith('sejarah'):
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*SEJARAH DESA DOMPYONG KULON*\n\nZaman dahulu kala daerah Gebang termasuk kedalam Kerajaan Cirebon yang disebut kefamilian Gebang yang dipimpin oleh Ki Gede atau Pangeran Sutajaya. Singkat cerita daerah Gebang termasuk daerah yang makmur dan membuat banyak orang pindah ke Gebang. Namun, semakin lama daerah Gebang menjadi sempit oleh orang yang berdatangan dan menetap, kemudian Ki Gede memerintahkan untuk memperluas daerah sebagai pemukiman. Ditetapkanlah sebuah daerah yang sekarang bernama blok Taman menjadi tempat pemukiman baru, tetapi di tengah-tengah pembangunan ada sebuah pohon yang di anggap angker dan terlarang, pohon tersebut bernama Pohon Widagori. \n\nKarena tidak ada yang bisa menebang pohon tersebut, Pangeran Sutajaya membuat sebuah sayembara yang isinya adalah 'Barang siapa yang bisa menebang pohon itu akan mendapatkan wilayah di sekitar pohon tersebut'. Sayembara itu terdengar sampai ke Kuningan dan terdengar oleh Raden Gentong yang berasal dari Cidahu, Kuningan. \nRaden Gentong yang bernama asli Ki Jembar, lantas berangkat dan berhasil menebang pohon Widagori tersebut. Pohon yang sudah ditebang tersebut kemudian dijadikan sebuah bedug yang terbuat dari Paku (Bahasa Jawa: Dom) Ketika sudah selesai bedug itu ditabuh sebanyak 3 kali dan berbunyi pyong... pyong... pyong... Dari peristiwa tersebut maka Raden Gentong menamakan daerah tersebut dengan nama Dompyong. \n\nSeiring berjalannya waktu, tahun 1983 Desa Dompyong dimekarkan menjadi 2 desa yaitu Desa Dompyong Kulon dan Dompyong Wetan.\n\n{back}")
                    return {"success": True}                              
                # SARANA DAN PRASARANA DESA
                if message_body == '4' or message_body.startswith('sarana'):
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*Jalan Desa*\nJalan desa merupakan salah satu prasarana yang sangat penting bagi masyarakat desa. Jalan desa berfungsi sebagai akses transportasi antara desa dengan kota atau desa lainnya.\n\n*Pusat Pemerintahan Desa*\nPusat pemerintahan desa merupakan tempat berkumpulnya pemerintahan desa dan masyarakat dalam melaksanakan berbagai kegiatan seperti rapat, musyawarah, dan sebagainya.\n\n*Sekolah*\nSekolah merupakan sarana pendidikan yang penting bagi masyarakat desa. Sekolah di desa berfungsi untuk memberikan pendidikan dan meningkatkan taraf hidup masyarakat desa.\n\n*Masjid*\nMasjid merupakan tempat ibadah yang penting bagi masyarakat desa. Masjid di desa berfungsi sebagai tempat berkumpulnya masyarakat dalam melaksanakan ibadah.\n\n*Lapangan Olahraga*\nLapangan olahraga merupakan sarana olahraga yang penting bagi masyarakat desa. Lapangan olahraga di desa berfungsi sebagai tempat untuk berolahraga dan mengembangkan potensi olahraga masyarakat desa.\n\n{back}")  
                    return {"success": True}                              
                # PROGRAM DESA
                if message_body =='5' or message_body.startswith('program'):
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"Layanan masih dalam perbaikan.\n\n{back}")  
                    return {"success": True}                              
                # NOT AVAILABLE
                if message_body not in ['1','2','3','4','5','menu','kembali','batal']:
                    tw.sendMsg(nomor_hp, f"Pilihan Anda tidak ada. Silakan kirim kembali berdasarkan opsi yang ada.")  
                    return {"success": True}

            elif act_faq[2] == 'org':
                # SOTK
                if message_body == 'a' or message_body == 'SOTK':
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*SUSUNAN ORGANISASI DAN TATA KERJA (SOTK)*\n\nAparatur Pemerintah Desa Dompyong Kulon Kecamatan Gebang Kabupaten Cirebon Provinsi Jawa Barat saat ini terdiri dari:\nKuwu:	KHUMAIDI\n\nUnsur Kesekretariatan\nSekretaris Desa:	AMAN TUJAHA\nKaur Keuangan:	SLAMET WIYADI\nKaur Tata Usaha dan Umum: WAWAN MUNAWAR\nKaur Perencanaan:	SYAHRIR RAMADHAN\n\nUnsur Teknis\nKasie Pemerintahan :	IMAN SUMANTRI\nKasie Pembangunan:	RAWUH\nKasie Kesejahteraan:	DEDI RAHMAT\n\nUnsur Kewilayahan\nKepala Dusun/Blok I:	TONI FATHONI\nKepala Dusun/Blok II :	M. DAHLIA HASAN SAPUTRA\nKepala Dusun/Blok III :	DIDING RYADI\nKepala Dusun/Blok IV :	DAMENDRA\nKepala Dusun/Blok V :	KADIR\n\n{back}")  
                    return {"success": True}                              
                # BPD
                if message_body == 'b':
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*BADAN PERMUSYAWARATAN DESA(BPD)*\n\nKetua:	Karnadi, S.Kom.I\nWakil Ketua:	H. Jaeni, S.Pd\nSekretaris:	Aris Rismawan, S.H.I\nAnggota:	Yahya, S.Pd\nAnggota:	M. Ari Maulana, S.Pd\nAnggota:	Nurudin\nAnggota:	Agan Setiadi\n\n{back}")
                    return {"success": True}                              
                # LPMD
                if message_body == 'c':
                    user_activity.activity = 'service_3#faq#done'
                    db.commit()
                    tw.sendMsg(nomor_hp, f"*LEMBAGA PEMBERDAYAAN MASYARAKAT DESA (LPMD)*\n\nKetua: KUSMAN\nWakil Ketua: BABANG H\nSekretaris: NADI SARNADI\nBendahara: RUKMIN\nBidang Persatuan & Kesatuan Masyarakat: SULAEMAN\nSeksi Pemanfaatan SDA & Lingdup: HAPID\nSeksi Pembangunan Sarana & Prasarana: AMAD\nSeksi Pembinaan Generasi Muda: CARSONO\nSeksi Kesehatan Masyarakat: PULUNG SUMARNA\nSeksi Pemberdayaan Perempuan: ODI CAHYADI\nSeksi Pembangunan Sarana & Prasarana Ii: KARIM\n\n{back}")
                    return {"success": True}                              
            
            elif act_faq[2] == 'sistem':
                # TENTANG CHATBOT
                if message_body == '1':
                    user_activity.activity = 'service_3#faq#done'
                    tw.sendMsg(nomor_hp, f"*[TENTANG SISTEM CHATBOT]*Chatbot dirancang dan dibangun oleh Komite Pengusaha Mikro Kecil Menengah Indonesia (KOPITU) Tahun 2024. Komite Pengusaha Mikro Kecil Menengah Indonesia Bersatu (KOPITU) dibentuk sebagai wadah di tingkat nasional yang menyatukan pelaku usaha dan pemangku kepentingan lain baik pemerintah maupun non pemerintah lintas sectoral dan multi sectoral untuk bersinergi meningkatkan kemampuan bersaing UMKM Indonesia\n\n{back}")
                    return {"success": True}
                # FITUR SAAT INI
                if message_body == '2':
                    user_activity.activity = 'service_3#faq#done'
                    tw.sendMsg(nomor_hp, f"*[FITUR CHATBOT SAAT INI]*\nBeberapa fitur sistem diantaranya adalah sebagai berikut:\n*1. Fitur pembuatan dokumen otomatis*\nWarga Dompyong Kulon dapat melakukan pengajuan formulir dengan melakukan registrasi data pada whatsapp berdasarkan data diri yang diperlukan, dimana data selanjutnya akan dikirim ke pihak administrasi desa untuk diurus lebih lanjut. Hingga update saat ini (04/2024) terdapat 4 jenis formulir yang dapat dibuat yakni diantaranya adalah formulir permohonan KTP, surat keterangan usaha, surat rekomendasi, dan surat keterangan tidak mampu\n*2. Fitur layanan administrasi*\nPengguna umum maupun warga Dompyong Kulon dapat melakukan komunikasi langsung dengan fitur customer service pada layanan administrasi untuk mendapatkan informasi langsung. \n*3. Fitur Informasi Umum*\nPengguna dapat membaca informasi mengenai desa Dompyong Kulon dimulai dari informasi umum, sejarah, sarana, hingga program-program yang dikembangkan di dalam desa.\n\n{back}")
                    return {"success": True}                
                # CARA MEMBUAT DOKUMEN
                if message_body == '3':
                    user_activity.activity = 'service_3#faq#done'
                    tw.sendMsg(nomor_hp, f"*[CARA MEMBUAT DOKUMEN LEWAT CHATBOT]*\nInformasi sedang dalam proses penulisan.\n\n{back}")
                    return {"success": True}   

            elif act_faq[2] == 'done' and message_body == 'kembali':
                tw.sendMsg(nomor_hp, f"*[INFORMASI DESA DOMPYONG KULON]*\nApa yang ingin Anda ketahui tentang Desa Dompyong Kulon?\n1. Tentang Desa\n2. Susunan Organisasi dan Tata Kerja (SOTK)\n3. Sejarah Singkat Desa\n4. Sarana dan Pra sarana Desa\n5. Program Desa")            
                user_activity.activity = 'service_3#faq#desa'
                db.commit()

        if user_activity.activity == 'finish' or message_body == 'batal':
            user_activity.activity = 'decision'
            db.commit()
            tw.sendMsg(nomor_hp, f"Selamat datang kembali!\nApa yang dapat kami bantu, {name}?\n1. Membuat Formulir Administrasi Desa Dompyong Kulon\n2. Chat dengan Customer Service\n3. Informasi Umum")
            return {"success": True}
    
        if message_body == 'menu' or message_body == 'Menu':
            user_activity.activity = 'decision'
            db.commit()
            tw.sendMsg(nomor_hp, f"Selamat datang kembali!\nApa yang dapat kami bantu, {name}?\n1. Membuat Formulir Administrasi Desa Dompyong Kulon\n2. Chat dengan Customer Service\n3. Informasi Umum")
            return {"success": True}
        
        if message_body == admin_acc:
            user_activity.activity = 'admin#decision'
            db.commit
            tw.sendMsg(nomor_hp, f"Masuk sebagai role administrator Dompyong Kulon.")
    return {"success": True}
    

