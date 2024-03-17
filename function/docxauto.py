from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
import provider.models

class Doc_Auto():
    # doc = Document()
    def __init__(self, db_con, model):
        # Create a new Document
        self.doc = Document()
        self.db_con = db_con
        self.model = model
    
    # kondisi dokumen
    def doc_id(self, nomor_hp):
        print(self.model.user_activity)
        useract = self.db_con.query(self.model.user_activity).filter_by(no_hp=nomor_hp).first()
        print(useract)
        return useract

    def wrapper_doc(self, nomor_hp, jenis_form):
        # panggil doc_id untuk cek query nomor telpon dan activity
        user_activity = self.doc_id(nomor_hp=nomor_hp)
        print(f'user id: {nomor_hp}')

        # MEMBUAT KTP
        if jenis_form == 'KTP':
            print("lancar")
            # # data form_ktp
            ktp_doc = self.db_con.query(self.model.form_ktp).filter_by(id_user_activity = user_activity.id).first()
            paragraph = self.doc.add_paragraph('FORMULIR PERMOHONAN KARTU TANDA PENDUDUK\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            self.doc.add_paragraph(
                'Yang bertanda tangan di bawah ini menerangkan dengan sebenar-benarnya bahwa: '
            )
            table = self.doc.add_table(rows=10, cols=2)
            hdr_cells = table.columns[0].cells
            hdr_cells[0].text = 'Nama\t\t:'
            hdr_cells[1].text = 'Nomor KK\t\t:'
            hdr_cells[2].text = 'NIK\t\t:'
            hdr_cells[3].text = 'Alamat\t\t:'
            hdr_cells[4].text = 'RT/RW\t\t:'
            hdr_cells[5].text = 'Desa\t\t:'
            hdr_cells[6].text = 'Kecamatan\t\t:'
            hdr_cells[7].text = 'Kabupaten/Kota\t:'
            hdr_cells[8].text = 'Provinsi\t\t:'
            hdr_cells[9].text = 'Tujuan\t\t:'
                        
            for cell in table.columns[0].cells:
                cell.width = Inches(1.5)

            cols_cells = table.columns[1].cells
            cols_cells[0].text = ktp_doc.nama
            cols_cells[1].text = ktp_doc.no_kk
            cols_cells[2].text = ktp_doc.nik
            cols_cells[3].text = ktp_doc.alamat
            cols_cells[4].text = ktp_doc.rtrw
            cols_cells[5].text = ktp_doc.desa
            cols_cells[6].text = ktp_doc.kecamatan           
            cols_cells[7].text = ktp_doc.kabupaten_kota
            cols_cells[8].text = ktp_doc.provinsi
            cols_cells[9].text = ktp_doc.tujuan_surat

            # doc.add_page_break()

            self.doc.add_paragraph(
                f'Nama tersebut adalah benar warga {ktp_doc.desa}, dan yang bersangkutan mengajukan surat keterangan pengajuan KTP untuk keperluan {ktp_doc.tujuan_surat}'
            )
            self.doc.add_paragraph(
                f'Demikian surat keterangan ini dibuat, atas perhatian dan kerjasamanya terima kasih.'
            )
            save = self.doc.save(f'doc/demo.docx')

        elif jenis_form == 'Usaha':
            print("lancar")
            # data form_ktp
            usaha_doc = self.db_con.query(self.model.form_usaha).filter_by(id_user_activity = user_activity.id).first()

            paragraph = self.doc.add_paragraph('SURAT IZIN USAHA\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # generate docx
            save = self.doc.save('demo.docx')

        elif jenis_form == 'Rekomendasi':
            print("lancar")
            # data form_ktp
            rec_doc = self.db_con.query(provider.models.form_rekomendasi).filter_by(id_user_activity = user_activity.id).first()
            
            paragraph = self.doc.add_paragraph('SURAT REKOMENDASI\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            self.doc.add_paragraph(
                'Yang bertanda tangan di bawah ini, Kepala Desa (Nama Desa) menerangkan dengan sebenar-benarnya bahwa: '
            )

            table = self.doc.add_table(rows=7, cols=2)
            hdr_cells = table.columns[0].cells
            hdr_cells[0].text = 'Nama\t\t:'
            hdr_cells[1].text = 'NIK\t\t:'
            hdr_cells[2].text = 'Tempat/Tanggal Lahir:'
            hdr_cells[3].text = 'Warganegara\t\t:'
            hdr_cells[4].text = 'Agama\t\t:'
            hdr_cells[5].text = 'Pekerjaan\t\t:'
            hdr_cells[6].text = 'Alamat\t:'
                        
            for cell in table.columns[0].cells:
                cell.width = Inches(1.5)

            cols_cells = table.columns[1].cells
            cols_cells[0].text = rec_doc.nama
            cols_cells[1].text = rec_doc.nik
            cols_cells[2].text = rec_doc.ttl
            cols_cells[3].text = rec_doc.warganegara
            cols_cells[4].text = rec_doc.agama
            cols_cells[5].text = rec_doc.pekerjaan
            cols_cells[6].text = rec_doc.alamat           
            
            self.doc.add_paragraph(
                f'Surat Rekomendasi ini dibuat untuk keperluan {rec_doc.tujuan_surat}.\nDemikian Rekomendasi ini dibuat dan diberikan kepada yang bersangkutan untuk dipergunakan sebagaimana mestinya.'
            )
            # generate docx
            save = self.doc.save(f'doc/KTP_rec_doc.docx')

        elif jenis_form == 'SKTM':
            print("lancar")
            # data form_ktp
            sktm_doc = self.db_con.query(provider.models.form_sktm).filter_by(id_user_activity = user_activity.id).first()

            paragraph = self.doc.add_paragraph('SURAT KETERANGAN TIDAK MAMPU\nNOMOR SURAT: ............')
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            self.doc.add_paragraph(
                'Yang bertanda tangan di bawah ini, Kepala Desa (Nama Desa) menerangkan dengan sebenar-benarnya bahwa: '
            )

            table = self.doc.add_table(rows=10, cols=2)
            hdr_cells = table.columns[0].cells
            hdr_cells[0].text = 'Nama\t\t:'
            hdr_cells[1].text = 'Nomor KK\t\t:'
            hdr_cells[2].text = 'NIK\t\t:'
            hdr_cells[3].text = 'Alamat\t\t:'
            hdr_cells[4].text = 'RT/RW\t\t:'
            hdr_cells[5].text = 'Desa\t\t:'
            hdr_cells[6].text = 'Kecamatan\t\t:'
            hdr_cells[7].text = 'Kabupaten/Kota\t:'
            hdr_cells[8].text = 'Provinsi\t\t:'
            hdr_cells[9].text = 'Tujuan\t\t:'
                        
            for cell in table.columns[0].cells:
                cell.width = Inches(1.5)

            cols_cells = table.columns[1].cells
            cols_cells[0].text = sktm_doc.nama
            cols_cells[1].text = sktm_doc.no_kk
            cols_cells[2].text = sktm_doc.nik
            cols_cells[3].text = sktm_doc.alamat
            cols_cells[4].text = sktm_doc.rtrw
            cols_cells[5].text = sktm_doc.desa
            cols_cells[6].text = sktm_doc.kecamatan           
            cols_cells[7].text = sktm_doc.kabupaten_kota
            cols_cells[8].text = sktm_doc.provinsi
            cols_cells[9].text = sktm_doc.tujuan_surat
            
            self.doc.add_paragraph(
                f'Surat ini dibuat untuk keperluan {sktm_doc.tujuan_surat}.\nDemikian SKTM ini dibuat dan diberikan kepada yang bersangkutan untuk dipergunakan sebagaimana mestinya.'
            )
            
            # generate docx
            save = self.doc.save('demo.docx')

        else:
            print("error!")

        return save
