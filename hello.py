from flask import Flask, render_template, request, url_for, redirect, session
from werkzeug import secure_filename
import os
from placidbconnect import connection
from passlib.hash import sha256_crypt as sha
from random import randint
from datetime import date
from time import localtime, strftime

app = Flask(__name__)
app.secret_key = 'SecretKey2012'

@app.route('/')
def index():
	if 'username' in session:
		return redirect(url_for('profile'))
	return render_template('index.html')

@app.route('/profile')
def profile():
	if 'username' in session:
		return render_template('profile.html', user=session['username'], login=True)
	else:
		return redirect(url_for('index'))

@app.route('/login', methods = ['POST'])
def login():
	if request.method == 'POST':
		user = request.form['username']
		password = request.form['password']
		
		curser, conn = connection()
		loginSQL = "SELECT * FROM users where user_name = %s;"
		curser.execute(loginSQL,(user,))
		result=curser.fetchone()

		if result == None:
			return redirect(url_for('index'))			

		if result[1]==user and sha.verify(password, result[2]) and 'username' not in session:
			session['username'] = user
			log_date = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
			log_time = strftime("%H:%M:%S", localtime())
			sql = "UPDATE users set last_login_date = %s, last_login_time = %s where user_name= %s;"
			curser.execute(sql,(log_date,log_time,user))
			conn.commit()
			conn.close()
			return redirect(url_for('profile'))

	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	if 'username' in session:
		session.pop('username', None)
	
	return redirect(url_for('index'))

@app.route('/uploader')
def uploader():
	if 'username' in session:
		return render_template('upload.html', login = True)
	else:
		return redirect(url_for('index'))

def allowed_file(filename):
	ALLOWED_EXTENSIONS = set(['jpeg', 'jpg','gif','png'])
	#ALLOWED_EXTENSIONS = set(['gif','png'])
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/fileLoader', methods=['POST'])
def Loader():
	if request.method == 'POST' and 'username' in session:
		if 'uploaded_file' not in request.files:
			return redirect(url_for('uploader'))

		file = request.files['uploaded_file']

		if file.filename == '':
			return redirect(url_for('uploader'))

		if allowed_file(file.filename) != True:
			return redirect(url_for('uploader'))

		file.save(os.path.join('photos',secure_filename(file.filename.rsplit('.',1)[0]+'_'+session['username']+'.'+file.filename.rsplit('.',1)[1])))
		return redirect(url_for('sucess'))

	return redirect(url_for('index'))

@app.route('/sucess')
def sucess():
	return render_template('sucess.html')

if __name__=='__main__':
	app.run(debug=True)