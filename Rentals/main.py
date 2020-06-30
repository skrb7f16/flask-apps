from flask import Flask,request,render_template,session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import bcrypt
from datetime import datetime
import string


with open("config.json", "r") as c:
    params = json.load(c)["params"]
local_server=True
app = Flask(__name__)
app.secret_key='this is a hard key'

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_url']
db = SQLAlchemy(app)

class Pg(db.Model):
    sno = db.Column( db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    accomodations = db.Column(db.String(4), nullable=False)
    price = db.Column(db.String(10), nullable=False)
    number = db.Column(db.String(10), nullable=False)
    description= db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    img_file= db.Column(db.String(30), nullable=False)

class Users(db.Model):
    user_id = db.Column( db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(15), nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)


class Contacts(db.Model):
    sno = db.Column( db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=True)



@app.route('/')
def home():
    pgs = Pg.query.filter_by().all()
    return render_template('index.html', params=params, pgs=pgs)

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/sent', methods=["GET","POST"])
def sent():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        message=request.form.get('message')
        number=request.form.get('phone')
        mess=Contacts(name=name, message=message,number=number, email=email, date=datetime.now())
        db.session.add(mess)
        db.session.commit()
        return "your message has been sent thank u"
    else:
        return "booooooooo"

@app.route('/book/<string:sno>', methods=["GET","POST"])
def booking(sno):
    pg = Pg.query.filter_by(sno=sno).first()
    return render_template('booking.html', pg=pg)

@app.route('/about/<string:sno>', methods=["GET"])
def about(sno):
    pg=Pg.query.filter_by(sno=sno).first()
    return render_template('about.html', pg=pg, params=params)




@app.route('/controlpanel', methods=["GET","POST"])
def control():
    pgs = Pg.query.all()
    contact = Contacts.query.filter_by().all()
    users = Users.query.filter_by().all()
    if 'user' in session and session['user']==params['username']:
        return render_template("dashboard.html", pgs=pgs, contact=contact, users=users)
    uname=request.form.get('email')
    password=request.form.get('password')
    if uname==params['username'] and password==params['password']:
        session['user']=uname
        return render_template("dashboard.html", pgs=pgs,contact=contact, users=users)
    else:
        message="Welcome to admin panel"
        msg = {"msg": message}
        return render_template("logadmin.html", msg=msg)

@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/register', methods=["GET","POST"])
def reg():
    if request.method == "POST":
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        uname=request.form.get('uname')
        email=request.form.get('email')
        password=bcrypt.hashpw(request.form.get('password').encode('UTF-8'), bcrypt.gensalt())
        conpassword=bcrypt.hashpw(request.form.get('cpassword').encode('UTF-8'), bcrypt.gensalt())
        dob=request.form.get('date')
        number=request.form.get('number')
        a=Users.query.filter_by(username=uname).count()
        if a==0:
            user=Users(first_name=fname, last_name=lname, email=email, password=password, date_of_birth=dob,number=number, username=uname)
            db.session.add(user)
            db.session.commit()
            return "hey u r registered"
        else:
            return "username exist"

@app.route('/userpanel', methods=["GET",'POST'])
def sigin():
    if 'renter' in session:
        return redirect('/userDisplay')
    else:
        message = ""
        msg = {"msg": message}
        return render_template('signin.html', msg=msg)

@app.route('/userDisplay', methods=["GET",'POST'])
def user():
    uname = request.form.get('uname')
    user = Users.query.filter_by(username=uname).first()
    password = request.form.get('password')
    if 'renter' in session:
        user = Users.query.filter_by(username=session['renter']).first()
        return render_template('user.html',user=user)
    elif bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        session['renter'] = uname
        return render_template('user.html', user=user)



@app.route('/useredit', methods=["GET","POST"])
def edit():
    return "still in progress for this template"


@app.route('/search' , methods=["GET","POST"])
def find():
    if request.method=="POST":
        name=request.form.get('search')
        searchitems=Pg.query.filter().all()
        pgs=[]
        for i in searchitems:
            if name in i.name:
                pgs.append(i)
        return render_template("index.html", params=params,pgs=pgs)
    else:
        return "booooooooooo"
@app.route('/logout')
def logout():
    session.pop('renter')
    return redirect('/userpanel')
@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    return redirect('/controlpanel')

@app.route('/booked/<string:sno>', methods=['GET','POST'])
def booked(sno):
    if request.method=='POST':
        email=request.form.get('email')
        phone=request.form.get('phone')
        name=request.form.get('name')
        category=request.form.get('category')
        time=request.form.get('time')
        age=request.form.get('age')
        foodType=request.form.get('foodType')
        pg=Pg.query.filter_by(sno=sno).first()
        data={
            'email':email,
            'phone':phone,
            'category':category,
            'time':time,
            'age':age,
            'foodtype':foodType,
            'name':name,
        }
        return render_template('bookconfirm.html', data=data, pg=pg)
@app.route('/booked/book/<string:sno>')
def changeInBooking(sno):
    return  'You have reached change page'

app.run(debug=True)