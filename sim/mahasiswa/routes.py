from email.mime import image
from flask import Flask, render_template, redirect, request, url_for, Blueprint, flash
from sim.mahasiswa.forms import Orang,login_org,Edit_org,pengaduan,edit_pengaduan,agenda_info
from sim.models import Tmahasiswa, Tpengaduan,Agenda_info
from sim import db, bcrypt,app
from flask_login import login_user,current_user,logout_user,login_required
import os
import secrets
from PIL import Image



rmahasiswa=Blueprint('rmahasiswa', __name__)

@rmahasiswa.route("/")
def rumah():
    return render_template("rumah.html")

@rmahasiswa.route("/tentang")
def tentang():
    return render_template("tentang.html")

@rmahasiswa.route("/daftar", methods=['GET', 'POST'])
def daftar():
    form=Orang()
    if (form.validate_on_submit()):
        pas_hash = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')# ini adalah variabel yang akan mengamankan pasword yang dimasukan dan nanti pasword yang sudah di amankan akan di panggil di line selanjutnya
        add_mahasiswa=Tmahasiswa(npm=form.npm.data, nama=form.nama.data, email=form.email.data, password=pas_hash, kelas=form.kelas.data, alamat=form.alamat.data)
        db.session.add(add_mahasiswa)
        db.session.commit()
        flash(f'Akun- {form.npm.data} berhasil daftar', 'primary')
      
        return redirect(url_for('rmahasiswa.login'))
    return render_template("daftar.html", form=form)

@rmahasiswa.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('rmahasiswa.rumah'))
    form=login_org()
    if form.validate_on_submit():
        ceknpm= Tmahasiswa.query.filter_by(npm=form.npm.data).first()
        if ceknpm and bcrypt.check_password_hash(ceknpm.password, form.password.data):
            login_user(ceknpm)
            flash('Selamat Datang Kembali', 'warning')
            return redirect(url_for('rmahasiswa.akun'))
        else:
            flash('Login Gagal, Periksa NPM dan Password kembali', 'danger')
    return render_template ("login.html",form=form)


@rmahasiswa.route("/akun")
@login_required # ini akan membuat halamanya hanya bisa dibuka saat user sudah login
def akun():
    return render_template('akun.html')

@rmahasiswa.route("/keluar")
def keluar():
    logout_user()
    return redirect(url_for('rmahasiswa.rumah'))

@rmahasiswa.route("/edit", methods=['GET','POST'])
@login_required
def edit():
    form = Edit_org()
    if form.validate_on_submit():# ini adalah sintak untuk mengupdate data yang akan dimasukan ke dalam database
        if form.foto.data:
            file_foto=simpan_foto(form.foto.data)
            current_user.foto=file_foto
        current_user.npm=form.npm.data
        current_user.nama=form.nama.data
        current_user.email=form.email.data
        current_user.kelas=form.kelas.data
        current_user.alamat=form.alamat.data
        sandi = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        current_user.password=sandi
        db.session.commit()
        flash('Data berhasil di rubah ','warning ')
        return redirect(url_for('rmahasiswa.edit'))
    elif request.method=="GET":# ini sintak untuk menampilkan data ke dalam database
        form.npm.data=current_user.npm
        form.nama.data=current_user.nama 
        form.email.data=current_user.email
        form.kelas.data=current_user.kelas
        form.alamat.data=current_user.alamat
        form.password.data=current_user.password
        
    return render_template ('edit.html',form=form)

#simpan foto 
def simpan_foto(form_foto):
    form = Edit_org()
    random_hex=secrets.token_hex(8  )
    f_name,f_ext=os.path.splitext(form_foto.filename)
    foto_fn = random_hex + f_ext
    foto_path = os.path.join(app.root_path,'sim/static/foto',foto_fn)# ini akan menyimpan foto yang diposting user
    # form_foto.save(foto_path)
    j = Image.open(form_foto)
    ubah_size=(300,300)
    j.thumbnail(ubah_size)
    j.save(foto_path)
    
    return foto_fn

@rmahasiswa.route("/laporan", methods=['GET','POST'])
@login_required
def laporan():
    dt_pengaduan = Tpengaduan.query.filter_by(mahasiswa_id=current_user.id)
    form = pengaduan()
    if form.validate_on_submit():
        
        add_laporan = Tpengaduan(subjek=form.subjek.data,kategori=form.kategori.data,detail_pengaduan=form.detail_pengaduan.data,mahasiswa=current_user)
        db.session.add(add_laporan)
        db.session.commit()
        flash('laporan telah diterima ','warning ')
        return redirect(url_for('rmahasiswa.laporan'))        
       
    return render_template('laporan.html',form=form,dt_pengaduan=dt_pengaduan)

@rmahasiswa.route("/editlaporan/<int:ed_id>/update", methods=['GET','POST'])
@login_required # ini akan membuat halamanya hanya bisa dibuka saat user sudah login
def edit_lapor(ed_id):# ed_id adalah id yang ada di database dan data yang di edit akan berdasarkan id nya
    form = edit_pengaduan()
    dt_pengaduan=Tpengaduan.query.get_or_404(ed_id)
    if request.method=="GET":# ini adalah sytak untuk menampilkan data 
        form.subjek.data=dt_pengaduan.subjek
        form.kategori.data=dt_pengaduan.kategori
        form.detail_pengaduan.data=dt_pengaduan.detail_pengaduan
    elif form.validate_on_submit():# ini sytak untuk mengubah data di dalam database
        dt_pengaduan.subjek=form.subjek.data
        dt_pengaduan.kategori=form.kategori.data
        dt_pengaduan.detail_pengaduan=form.detail_pengaduan.data
        db.session.commit()
        flash('Laporan telah direvisi :)','warning')
        return redirect(url_for('rmahasiswa.laporan'))
    return render_template('editlaporan.html',form=form)

@rmahasiswa.route("/delete/<id>", methods=['GET','POST'])
@login_required # ini akan membuat halamanya hanya bisa dibuka saat user sudah login
def cabut_lapor(id):
    hapus =Tpengaduan.query.get(id)
    db.session.delete(hapus)
    db.session.commit()
    flash('Laporan telah sudah dicabut :)','warning')
    return redirect(url_for('rmahasiswa.laporan'))

@rmahasiswa.route("/posting", methods=['GET','POST'])
@login_required
def agenda_inf():
    form = agenda_info()
    if form.validate_on_submit(): 
        add_agenda = Agenda_info(subjek=form.subjek.data,caption=form.caption.data)
        db.session.add(add_agenda)
        db.session.commit()
        flash('Sudah di posting ','warning ')
        return redirect(url_for('rmahasiswa.agenda_inf'))  
    return render_template('tambahagenda.html',form=form)#, info_agenda=info_agenda)

@rmahasiswa.route("/agenda", methods=['GET','POST'])
def informasi():
    info_agenda = Agenda_info.query.all()
    
    return render_template("agenda_info.html",info=info_agenda)