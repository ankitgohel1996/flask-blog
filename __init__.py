from flask import Flask,request,url_for,render_template,abort,redirect,flash,session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@localhost/flasktest"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'oxoa'
app.config['DEBUG'] = True 
db=SQLAlchemy(app)

class user(db.Model):
	u_id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	password = db.Column(db.String(100))

	def __init__(self,name,email,password):
		self.name = name
		self.email = email
		self.password = password

class posts(db.Model):
	post_id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(100))
	content = db.Column(db.String(500))
	user_id= db.Column(db.Integer, db.ForeignKey(user.u_id))

	def __init__(self,title,content,user_id):
		self.title = title
		self.content = content
		self.user_id=user_id

db.create_all()

@app.route('/',methods = ['POST','GET'])
def login():
	if request.method == 'GET':
		if session.get('userID') is not None:
			temp = user.query.filter_by(u_id = session ['userID']).first()
			loggedinuser = temp.name
			return redirect(loggedinuser)
		else:
			return render_template('login.html')
	elif request.method == 'POST':
		loginuser = request.form['username']
		loginpassword = request.form['password']
		currentuser = user.query.filter_by(name = loginuser).first()

		if currentuser is not None:
			if currentuser.password == loginpassword:
				session['userID'] = currentuser.u_id
				return redirect(loginuser)
			else:
				return render_template('login.html')
		else:
			return render_template('login.html',success = 'User does not exist')

@app.route('/register',methods = ['POST','GET'])
def register():
	if request.method == 'GET':
		return render_template('register.html')
	elif request.method == 'POST':
		tempuser = user(request.form['username'],request.form['emailid'],request.form['password'])
		tempusername = request.form['username']
		alreadyexisting = user.query.filter_by(name=tempusername).count()

		if(alreadyexisting > 0):
			return render_template('register.html',alreadyexists = 'This username is already taken')
		else:
			db.session.add(tempuser)
			db.session.commit()
			render_template('login.html',success = 'You have successfully registered')
			return redirect(url_for('login'))


@app.route('/<user>', methods = ['GET','POST'])
def profile(user):
	if session.get('userID') is not None:
		if request.method == 'GET':
			userposts = posts.query.filter_by(user_id = session['userID'])
			return render_template('profile.html',user=user, userposts = userposts)
		elif request.method == 'POST':
			tempblogpost = posts(request.form['title'],request.form['content'],session['userID'])
			db.session.add(tempblogpost)
			db.session.commit()

			userposts = posts.query.filter_by(user_id = session['userID'])
			return render_template('profile.html',user=user, userposts = userposts)
	else:
		return redirect('/')

@app.route('/<user>/delete/<postid>')
def delete(user,postid):
	deletepost = posts.query.filter_by(post_id=postid).first()
	db.session.delete(deletepost)
	db.session.commit()

	userposts = posts.query.filter_by(user_id = session['userID'])
	render_template('profile.html',user=user, userposts=userposts)
	return redirect(user)

@app.route('/<user>/edit/<postid>', methods =['GET','POST'])
def edit(user,postid):
	if request.method == 'GET':
		currentpost = posts.query.filter_by(post_id = postid).first()
		currenttitle = currentpost.title
		currentcontent = currentpost.content
		return render_template('edit.html',currenttitle=currenttitle, currentcontent = currentcontent,user =user,postid=postid)
	elif request.method == 'POST':
		currentpost = posts.query.filter_by(post_id = postid).first()
		currentpost.title = request.form['title']
		currentpost.content = request.form['content']
		db.session.commit()
		
		userposts = posts.query.filter_by(user_id = session['userID'] )
		render_template('profile.html',user=user, userposts = userposts)
		return redirect(user)

@app.route('/<user>/logout')
def logout(user):
	session.pop('userID', None)
	return redirect('/') 	 

if __name__=='__main__':
	app.run()
