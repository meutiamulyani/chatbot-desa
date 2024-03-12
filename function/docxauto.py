from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
import provider.models

class Doc_Auto():
    # doc = Document()
    def __init__(self, db_con):
        # Create a new Document
        self.doc = Document()
        self.db_con = db_con
    
    # kondisi dokumen
    def doc_id(self, nomor_hp):
        # Heading judul form
        user = self.db_con.query(provider.models.user_activity).filter_by(no_hp=nomor_hp).first()
        if user:
            print('connected')
        else:
            print('data tidak ada.')
        return user
    
    def wrapper_doc(self, user_id, jenis_form):
        # panggil doc_id untuk cek query nomor telpon dan activity
        user = self.doc_id(user_id=user_id)
        print(user.no_hp)

        # MEMBUAT KTP
        if jenis_form == 'KTP':
            print("lancar")
            # data form_ktp
            ktp_doc = self.db_con.query(provider.models.form_ktp).filter_by(id_user_activity = user.id).first()

            paragraph = self.doc.add_paragraph('SURAT KETERANGAN TIDAK MAMPU\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            self.doc.add_paragraph(
                'Yang bertanda tangan di bawah ini menerangkan dengan sebenar-benarnya bahwa: '
            )
            table = self.doc.add_table(rows=3, cols=2)
            hdr_cells = table.columns[0].cells
            hdr_cells[0].text = 'Nama\t\t:'
            hdr_cells[1].text = 'KTP\t\t:'
            hdr_cells[2].text = 'Alamat\t\t:'
            for cell in table.columns[0].cells:
                cell.width = Inches(1.5)

            cols_cells = table.columns[1].cells
            cols_cells[0].text = ktp_doc.nama
            cols_cells[1].text = ktp_doc.nik
            cols_cells[2].text = ktp_doc.alamat

            # doc.add_page_break()

            self.doc.add_paragraph(
                f'Nama tersebut adalah benar warga {ktp_doc.desa}, dan yang bersangkutan mengajukan surat keterangan tidak mampu untuk keperluan {ktp_doc.tujuan_surat}'
            )
            self.doc.add_paragraph(
                f'Demikian surat keterangan ini dibuat, atas perhatian dan kerjasamanya terima kasih.'
            )
            save = self.doc.save('demo.docx')

        elif jenis_form == 'Usaha':
            print("lancar")
            # data form_ktp
            usaha_doc = self.db_con.query(provider.models.form_usaha).filter_by(id_user_activity = user.id).first()

            paragraph = self.doc.add_paragraph('SURAT IZIN USAHA\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # generate docx
            save = self.doc.save('demo.docx')

        elif jenis_form == 'Rekomendasi':
            print("lancar")
            # data form_ktp
            rec_doc = self.db_con.query(provider.models.form_rekomendasi).filter_by(id_user_activity = user.id).first()

            paragraph = self.doc.add_paragraph('SURAT REKOMENDASI\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # generate docx
            save = self.doc.save('demo.docx')

        elif jenis_form == 'SKTM':
            print("lancar")
            # data form_ktp
            sktm_doc = self.db_con.query(provider.models.form_sktm).filter_by(id_user_activity = user.id).first()

            paragraph = self.doc.add_paragraph('SURAT REKOMENDASI\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # generate docx
            save = self.doc.save('demo.docx')

        else:
            print("error!")


        return save
        # if jenis_form == 'Usaha':
        #     self.doc_usaha(user_id=user_id)
        # if jenis_form == 'Rekomendasi':
        #     self.doc_rekomendasi(user_id=user_id)
        # if jenis_form == 'SKTM':
        #     self.doc_sktm(user_id=user_id)
        return

    # Save the document
    # doc.save('my_document.docx')

# panggil di main.py
# generate = Doc_Auto(db_con=db_dependency)
# result_docauto = generate.wrapper_doc(user_activity.no_hp, act[3]) #<- buat status pembuatan form