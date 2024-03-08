from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from provider.db import Base
from sqlalchemy.orm import relationship

class user_activity(Base):
    __tablename__ = 'user_activity'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    no_hp = Column(String, unique=True)
    activity = Column(String)
    form_rekomendasi = relationship('form_rekomendasi', back_populates='user_activity')
    form_usaha = relationship('form_usaha', back_populates='user_activity')
    form_ktp = relationship('form_ktp', back_populates='user_activity')
    form_sktm = relationship('form_sktm',back_populates='user_activity')
    

class form_ktp(Base):
    __tablename__ = 'form_ktp'

    id_form_ktp = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user_activity = Column(Integer, ForeignKey('user_activity.id'))
    user_activity = relationship('user_activity', back_populates='form_ktp')
    nama = Column(String)
    no_kk = Column(String)
    nik = Column(String)
    alamat = Column(String)
    rtrw = Column(String)
    desa = Column(String)
    kecamatan = Column(String)
    kabupaten_kota = Column(String)
    provinsi = Column(String)
    tujuan_surat = Column(String)

class form_usaha(Base):
    __tablename__ = 'form_usaha'

    id_form_usaha = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user_activity = Column(Integer, ForeignKey('user_activity.id'))
    user_activity = relationship('user_activity', back_populates='form_usaha')
    nama = Column(String)
    nik = Column(String)
    jenis_kelamin = Column(String)
    ttl = Column(String)
    alamat = Column(String)
    pekerjaan = Column(String)
    rtrw = Column(String)
    nama_usaha = Column(String)
    start_usaha = Column(String)
    alamat_usaha = Column(String)
    tujuan_surat = Column(String)

class form_rekomendasi(Base):
   __tablename__ = 'form_rekomendasi'

   id_form_rekomendasi = Column(Integer, primary_key=True, index=True, autoincrement=True)
   id_user_activity = Column(Integer, ForeignKey('user_activity.id'))
   user_activity = relationship('user_activity', back_populates='form_rekomendasi')
   nama = Column(String)
   nik = Column(String)
   ttl = Column(String)
   warganegara = Column(String)
   agama = Column(String)
   pekerjaan = Column(String)
   alamat = Column(String)
   tujuan_surat = Column(String)

class form_sktm(Base):
    __tablename__ = 'form_sktm'

    id_form_sktm = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user_activity = Column(Integer, ForeignKey('user_activity.id'))
    user_activity = relationship('user_activity', back_populates='form_sktm')   

    nama = Column(String)
    nik = Column(String)
    jenis_kelamin = Column(String)
    ttl = Column(String)
    warganegara = Column(String)
    agama = Column(String)
    pekerjaan = Column(String)
    status = Column(String)
    alamat = Column(String)
    tujuan_surat = Column(String)