from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash as passhash
from werkzeug.security import check_password_hash as passcheck
from yaml import load, FullLoader
from os import urandom
from datetime import datetime
# App Enablings
app = Flask(__name__)
Bootstrap(app)
mysql = MySQL(app)
CKEditor(app)

# MySQL Configuration
db = load(open('db.yaml'), Loader=FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['SECRET_KEY'] = urandom(24)
app.config['CURSORCLASS'] = 'CursorDict'

# ============= ROUTES ============= #
@app.route('/')
def index():
	cur = mysql.connection.cursor()
	userqeury = cur.execute("SELECT * FROM userQuery")
	if userqeury > 0:
		u_queries = cur.fetchall()
		cur.close()

	cur = mysql.connection.cursor()
	docquery = cur.execute("SELECT * FROM docQuery")
	if docquery > 0:
		d_queries = cur.fetchall()
		cur.close()
		return render_template('index.html', u_queries=u_queries, d_queries=d_queries)

	cur.close()
	return render_template('index.html', u_queries=None, d_queries=None)

@app.route('/register/user/', methods=['GET', 'POST'])
def user_reg():
	if request.method == 'POST':
		form = request.form
		if form['password'] == form['confirm_password']:
			firstname = form['firstname']
			lastname = form['lastname']
			username = form['username']
			password = passhash(form['password'])
			gender = form['gender']
			postcode = form['post_code']
			contact_number = form['contact_number']
			state = form['state']
			city = form['city']
			email = form['email']
			lat = form['lati'][0:9]
			longg = form['longi'][0:9]
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO user(firstname, lastname, username, password, gender, postcode, contact_number, state, city, email, lat, longg) \
			 VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (firstname, lastname, username, password, gender, postcode, contact_number, state, city, email, lat, longg))
			mysql.connection.commit()
			cur.close()
			flash('Registration Successfull ! You can Now Login', 'success')
			return redirect('/login/user/')

		else:
			flash('Passwords Do Not Match', 'danger')
			return render_template('register-user.html')
	return render_template('register-user.html')

@app.route('/register/doc/', methods=['GET', 'POST'])
def doc_reg():
	if request.method == 'POST':
		form = request.form
		if form['password'] == form['confirm_password']:
			firstname = form['firstname']
			lastname = form['lastname']
			contact_number = form['contact_number']
			email = form['email']
			username = form['username']
			password = passhash(form['password'])
			speciality = form['speciality']
			clinic = form['clinic']
			hospital = form['hospital']
			link = form['link']
			gender = form['gender']
			postcode = form['post_code']
			lat = form['lati'][0:9]
			longg = form['longi'][0:9]
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO doctor(firstname, lastname, contact_number, email, username, password, speciality, clinic, hospital, link, gender, postcode, lat, longg) \
			 VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (firstname, lastname, contact_number, email, username, password, speciality, clinic, hospital, link, gender, postcode, lat, longg))
			mysql.connection.commit()
			cur.close()
			flash('Registration Successfull ! You can Now Login', 'success')
			return redirect('/login/doc/')
	return render_template('register-doc.html')

@app.route('/login/')
def function():
	return render_template('login.html')

@app.route('/login/user/', methods=['GET', 'POST'])
def user_login():
	if request.method == 'POST':
		userDetails = request.form
		user_username = userDetails['username']
		user_password = userDetails['password']

		cur = mysql.connection.cursor()
		database = cur.execute("SELECT * FROM user WHERE username=%s", [(user_username)])
		if database > 0:
			user = cur.fetchone()
			checker = passcheck(user[4], user_password)
			if checker:
				session['login'] = True
				session['firstname'] = user[1]
				session['lastname'] = user[2]
				session['user'] = 'user'
				session['username'] = user[3]
				flash(f"Welcome {session['firstname']} !!! Your Login is Successfull", "success")
				return redirect('/')

			else:
				cur.close()
				flash('Wrong Password !!! Please Try Again', 'danger')
				return render_template('login.html')

		else:
			cur.close()
			flash('No User Found !!! Please Check Username Again', 'danger')
			return render_template('login.html')

	return render_template('login.html')

@app.route('/login/doc/', methods=['POST', 'GET'])
def doc_login():
	if request.method == 'POST':
		userDetails = request.form
		user_username = userDetails['username']
		user_password = userDetails['password']
		print(user_password)

		cur = mysql.connection.cursor()
		database = cur.execute("SELECT * FROM doctor WHERE username=%s", [(user_username)])
		if database > 0:
			user = cur.fetchone()
			checker = passcheck(user[4], user_password)
			if checker:
				session['login'] = True
				session['firstname'] = user[1]
				session['lastname'] = user[2]
				session['user'] = 'doctor'
				session['username'] = user[5]
				session['speciality'] = user[7]
				flash(f"Welcome {session['firstname']} !!! Your Login is Successfull", "success")
				return redirect('/')

			else:
				cur.close()
				flash('Wrong Password !!! Please Try Again', 'danger')
				return render_template('login.html')

		else:
			cur.close()
			flash('No User Found !!! Please Check Username Again', 'danger')
			return render_template('login.html')

	return render_template('login.html')

@app.route('/write-query/public/', methods=['GET', 'POST'])
def pub_query():
	if request.method == 'POST':
		if session['user'] == 'user':
			details = request.form
			title = details['title']
			body = details['body']
			spcl = details['speciality']
			author = session['firstname'] + ' ' + session['lastname']
			username = session['username']
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO userQuery(author, title, body, specialisation, username) VALUES(%s, %s, %s, %s, %s);", (author, title, body, spcl, username))
			mysql.connection.commit()
			cur.close()

			flash('Query Submitted Successfully', 'success')
			return redirect('/')

		elif session['user'] == 'doctor':
			details = request.form
			title = details['title']
			body = details['body']
			spcl = details['speciality']
			author = session['firstname'] + ' ' + session['lastname']
			username = session['username']
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO docQuery(author, title, body, specialisation, username) VALUES(%s, %s, %s, %s, %s);", (author, title, body, spcl, username))
			mysql.connection.commit()
			cur.close()

			flash('Suggestion Submitted Successfully', 'success')
			return redirect('/')
	return render_template('write-query.html')

@app.route('/write-query/private/', methods=['GET', 'POST'])
def priv_query():
	if request.method == 'POST':
		formdet = request.form
		username = session['username']
		speciality = formdet['speciality']
		title = formdet['title']
		body = formdet['body']
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO doc_received(user_username, speciality, request_title, request_body) VALUES(%s, %s, %s, %s)", (username, speciality, title, body))
		mysql.connection.commit()
		cur.close()
		flash(f'Request Sent to all Doctors of Speciality - {speciality}', 'success')
		return redirect('/')
	return render_template('write-query.html')

@app.route('/user/view-query/<int:id>/')
def view_user_query(id):
	cur = mysql.connection.cursor()
	resultquery = cur.execute("SELECT * FROM userQuery WHERE query_id={}".format(id))
	if resultquery > 0:
		query = cur.fetchone()
		resultcomments = cur.execute("SELECT * FROM userpost_comments WHERE post_id={}".format(id))
		if resultcomments > 0:
			comments = cur.fetchall()
			return render_template('view-query.html', query=query, comments=comments, commNumber=resultcomments, querytype='User')
		return render_template('view-query.html', query=query, comments=None, commNumber=None, querytype=None)
	return 'No Query Found'

@app.route('/doc/view-query/<int:id>/')
def view_doc_query(id):
	cur = mysql.connection.cursor()
	resultquery = cur.execute("SELECT * FROM docQuery WHERE query_id={}".format(id))
	if resultquery > 0:
		query = cur.fetchone()
		resultcomments = cur.execute("SELECT * FROM docpost_comments WHERE post_id={}".format(id))
		if resultcomments > 0:
			comments = cur.fetchall()
			return render_template('view-query.html', query=query, comments=comments, commNumber=resultcomments, querytype='Doctor')
		return render_template('view-query.html', query=query, comments=None, commNumber=None, querytype=None)
	return 'No Query Found'

@app.route('/doc/view-request/<int:id>/')
def view_doc_request(id):
	cur = mysql.connection.cursor()
	resultquery = cur.execute("SELECT * FROM doc_received WHERE request_id={}".format(id))
	if resultquery > 0:
		request = cur.fetchone()
		return render_template('view-request.html', request=request)
	return render_template('view-query.html', request=None)

@app.route('/user/<username>/')
def userProfile(username):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM user WHERE username='{}'".format(username))
	if result > 0:
		user = cur.fetchone()
		return render_template('user.html', user=user)
	return "User Not Found"

@app.route('/doc/<username>/')
def docProfile( username):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM doctor WHERE username='{}'".format(username))
	if result > 0:
		doc = cur.fetchone()
		return render_template('doctor.html', doc=doc)
	return "Doctor Not Found"

@app.route('/user/<username>/my-queries/')
def my_queries(username):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM userQuery WHERE username='{}'".format(username))
	mysql.connection.commit()
	if result > 0:
		queries = cur.fetchall()
		return render_template('my-queries.html', queries=queries)

	return render_template('my-queries.html', queries=None)

@app.route('/doc/<speciality>/requests/')
def rec_requests(speciality):
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * FROM doc_received WHERE speciality ='{}'".format(speciality))
	if result > 0:
		requests = cur.fetchall()
		return render_template('requests.html', requests=requests)

	return render_template('requests.html', requests=None)

@app.route('/user/view-query/<int:query_id>/comment/', methods=['GET', 'POST'])
def userpost_comment(query_id):
	if request.method == 'POST':
		comment = request.form
		post_id = query_id
		commentor_fullname = session['firstname'] + ' ' + session['lastname']
		commentor_username = session['username']
		commentator_type = session['user']
		comBody = comment['body']
		post_time = datetime.now().strftime("%H:%M:%S")
		post_date = str(datetime.now().date())
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO userpost_comments(post_id, commentor_fullname, commentor_username, commentator_type, comment, post_time, post_date) \
			VALUES(%s, %s, %s, %s, %s, %s, %s)", (post_id, commentor_fullname, commentor_username, commentator_type, comBody, post_time, post_date))
		mysql.connection.commit()
		cur.close()
		flash('Comment Posted', 'success')
	return redirect('/user/view-query/{}/'.format(query_id))

@app.route('/doc/view-query/<int:query_id>/comment/', methods=['GET', 'POST'])
def docpost_comment(query_id):
	if request.method == 'POST':
		comment = request.form
		post_id = query_id
		commentor_fullname = session['firstname'] + ' ' + session['lastname']
		commentor_username = session['username']
		commentator_type = session['user']
		comBody = comment['body']
		post_time = datetime.now().strftime("%H:%M:%S")
		post_date = str(datetime.now().date())
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO docpost_comments(post_id, commentor_fullname, commentor_username, commentator_type, comment, post_time, post_date) \
			VALUES(%s, %s, %s, %s, %s, %s, %s)", (post_id, commentor_fullname, commentor_username, commentator_type, comBody, post_time, post_date))
		mysql.connection.commit()
		cur.close()
		flash('Comment Posted', 'success')
	return redirect('/doc/view-query/{}/'.format(query_id))

@app.route('/logout/')
def logout():
	session.clear()
	flash('You Have Been Logged Out', 'info')
	return redirect('/')

if __name__ == '__main__':
	app.run(port=8080, debug=True)
