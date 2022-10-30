from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from database.db import db, get_all_collection, storage
from firebase_admin import firestore
from functools import wraps
# ===============================================

# Starter Template Flask
# By Makassar Coding

# ================================================
# Menentukan Nama Folder Penyimpanan Asset
app = Flask(__name__, static_folder='static', static_url_path='')
# Untuk Menggunakan flash pada flask
app.secret_key = 'iNiAdalahsecrEtKey'
# Untuk Mentukan Batas Waktu Session
app.permanent_session_lifetime = datetime.timedelta(days=7)
# Menentukan Jumlah Maksimal Upload File
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash('Login Dulu Bosscu', 'danger')
            return redirect(url_for('login'))
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mahasiswa')
@login_required
def mahasiswa():

    daftar_mahasiswa = get_all_collection('mahasiswa')

    return render_template('mahasiswa/mahasiswa.html',daftar_mahasiswa=daftar_mahasiswa)

@app.route('/mahasiswa/tambah', methods=['GET', 'POST'])
def tambah_mahasiswa():
    if request.method == 'POST':
        # tampung data di dictionary
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'nama_lengkap': request.form['nama_lengkap'],
            'nim': request.form['nim'],
            'jurusan': request.form['jurusan'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'status': request.form['status'],
            'jenis_kelamin': request.form['jenis_kelamin'],
        }

        if 'image' in request.files and request.files['image']:
            image = request.files['image']
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            filename = image.filename
            lokasi = f"mahasiswa/{filename}"
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                storage.child(lokasi).put(image)
                data['photoURL'] = storage.child(lokasi).get_url(None)
            else:
                flash("Foto tidak diperbolehkan", "danger")
                return redirect(url_for('mahasiswa'))
        # masukkan data ke database
        db.collection('mahasiswa').document().set(data)

        # kembali ke halaman mahasiswa
        flash('Berhasil Menambahkan Data', 'success')
        return redirect(url_for ('mahasiswa'))
    jurusan = get_all_collection('jurusan')
    return render_template('mahasiswa/tambah_mahasiswa.html', jurusan=jurusan)

# read
@app.route('/mahasiswa/<uid>')
def lihat_mahasiswa(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('mahasiswa/lihat_mahasiswa.html', data=mahasiswa)

# update

@app.route('/mahasiswa/edit/<uid>', methods=['GET', 'POST'])
def edit_mahasiswa(uid):
    if request.method == 'POST':
        # tampung data di dictionary
        data = {
            'nama_lengkap': request.form['nama_lengkap'],
            'nim': request.form['nim'],
            'jurusan': request.form['jurusan'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'status': request.form['status'],
            'jenis_kelamin': request.form['jenis_kelamin'],
        }
        # masukkan data ke database
        db.collection('mahasiswa').document(uid).update(data)

        # kembali ke halaman mahasiswa
        flash('Berhasil Memperbaharui Data', 'success')
        return redirect(url_for ('mahasiswa'))
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('mahasiswa/edit_mahasiswa.html', data=mahasiswa)

# hapus
@app.route('/mahasiswa/hapus/<uid>')
def hapus_mahasiswa(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).delete()
    flash('Berhasil Menghapus Data', 'danger')
    return redirect(url_for('mahasiswa'))

# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # tangkap data untuk di cek
        data = {
            'username' : request.form['username'],
            'password' : request.form['password']
        }
     
        # cek data di database
        users_ref = db.collection('users').where('username', '==', data['username']).stream()
        user = {}
        for use in users_ref:
            user = use.to_dict()

        if user:
        # jika ada cek password
            if check_password_hash(user['password'], data['password']):
        # setelah cek simpan ke dalam session
        # setelah disimpan return ke halaman mahasiswa
                session['user'] = user
                flash('Berhasil Login', 'success')
                return redirect(url_for('mahasiswa'))
            else:
                flash('Username/Password Tidak Sesuai', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Username dan Password Tidak Sesuai', 'danger')
            return redirect(url_for('login'))

    if 'user' in session:
        return redirect(url_for('mahasiswa'))
    return render_template('login.html')


# register
@app.route('/register',  methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'username': request.form['username'].lower(),
            'email': request.form['email'].lower(),
        }
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']

        if confirmpassword != password:
            flash('Password Tidak Sesuai', 'danger')
            return redirect(url_for('register'))

        users_ref = db.collection('users').where('username', '==', data ['username']).stream()
        user = {}
        for use in users_ref:
            user = use.to_dict()

        if user:
            flash('Username Sudah Terdaftar', 'danger')
            return redirect(url_for('register'))

        data['password'] = generate_password_hash(password, 'sha256')

        db.collection('users').document().set(data)
        flash('Pendaftaran Berhasil', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


# ========================================================================================================
@app.route('/jurusan', methods=['POST', 'GET'])
@login_required
def jurusan():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'jurusan' : request.form['jurusan']
        }

        db.collection('jurusan').document().set(data)
        flash('Berhasil Menambahkan Jurusan', 'success')
        return redirect(url_for('jurusan'))
    daftar_jurusan = get_all_collection('jurusan')
    return render_template('jurusan/jurusan.html', data=daftar_jurusan)

@app.route('/jurusan/hapus/<uid>')
@login_required
def hapus_jurusan(uid):
    jurusan = db.collection('jurusan').document(uid).delete()
    flash('Berhasil Menghapus Jurusan', 'danger')
    return redirect(url_for('jurusan'))


@app.route('/jurusan/edit', methods=['POST'])
@login_required
def edit_jurusan():
    if request.method == 'POST':
        uid = request.form['id_jurusan']
        data = {
            'jurusan' : request.form['nama_jurusan']
        }
        db.collection('jurusan').document(uid).update(data)
        flash('Berhasil Memperbaharui Jurusan', 'success')
        return redirect(url_for ('jurusan'))

# ===========================================================================================================

@app.route('/dosen')
@login_required
def dosen():

    daftar_dosen = get_all_collection('dosen')

    return render_template('dosen/dosen.html',daftar_dosen=daftar_dosen)

@app.route('/dosen/tambah', methods=['GET', 'POST'])
def tambah_dosen():
    if request.method == 'POST':
        # tampung data di dictionary
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'nama_lengkap': request.form['nama_lengkap'],
            'program_studi': request.form['program_studi'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'status': request.form['status'],
            'jenis_kelamin': request.form['jenis_kelamin'],
        }

        if 'image' in request.files and request.files['image']:
            image = request.files['image']
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            filename = image.filename
            lokasi = f"dosen/{filename}"
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                storage.child(lokasi).put(image)
                data['photoURL'] = storage.child(lokasi).get_url(None)
            else:
                flash("Foto tidak diperbolehkan", "danger")
                return redirect(url_for('dosen'))
        # masukkan data ke database
        db.collection('dosen').document().set(data)

        # kembali ke halaman mahasiswa
        flash('Berhasil Menambahkan Data', 'success')
        return redirect(url_for ('dosen'))
    program_studi = get_all_collection('program_studi')
    return render_template('dosen/tambah_dosen.html', program_studi=program_studi)

@app.route('/dosen/<uid>')
def lihat_dosen(uid):
    dosen = db.collection('dosen').document(uid).get().to_dict()
    return render_template('dosen/lihat_dosen.html', data=dosen)

# update

@app.route('/dosen/edit/<uid>', methods=['GET', 'POST'])
def edit_dosen(uid):
    if request.method == 'POST':
        # tampung data di dictionary
        data = {
            'nama_lengkap': request.form['nama_lengkap'],
            'program_studi': request.form['_program_studi'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'status': request.form['status'],
            'jenis_kelamin': request.form['jenis_kelamin'],
        }
        # masukkan data ke database
        db.collection('dosen').document(uid).update(data)

        # kembali ke halaman mahasiswa
        flash('Berhasil Memperbaharui Data Dosen', 'success')
        return redirect(url_for ('dosen'))
    dosen = db.collection('dosen').document(uid).get().to_dict()
    return render_template('dosen/edit_dosen.html', data=dosen)

# hapus
@app.route('/dosen/hapus/<uid>')
def hapus_dosen(uid):
    mahasiswa = db.collection('dosen').document(uid).delete()
    flash('Berhasil Menghapus Data Dosen', 'danger')
    return redirect(url_for('dosen'))

# ==============================================================================================

@app.route('/program_studi', methods=['POST', 'GET'])
@login_required
def program_studi():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'program_studi' : request.form['program_studi']
        }

        db.collection('program_studi').document().set(data)
        flash('Berhasil Menambahkan Program Studi', 'success')
        return redirect(url_for('program_studi'))
    daftar_program_studi = get_all_collection('program_studi')
    return render_template('program_studi/program_studi.html', data=daftar_program_studi)

@app.route('/program_studi/hapus/<uid>')
@login_required
def hapus_program_studi(uid):
    program_studi = db.collection('program_studi').document(uid).delete()
    flash('Berhasil Menghapus Program Studi', 'danger')
    return redirect(url_for('program_studi'))


@app.route('/program_studi/edit', methods=['POST'])
@login_required
def edit_program_studi():
    if request.method == 'POST':
        uid = request.form['id_program_studi']
        data = {
            'program_studi' : request.form['nama_program_studi']
        }
        db.collection('program_studi').document(uid).update(data)
        flash('Berhasil Memperbaharui Program Studi', 'success')
        return redirect(url_for ('program_studi'))


@app.route('/cek_session')
def cek_session():
    return jsonify(session['user'])


# Untuk Menjalankan Program Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)