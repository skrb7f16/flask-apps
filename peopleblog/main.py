from flask import Flask,request,render_template,session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import bcrypt
from datetime import datetime
from impfunc import filtering
import math

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

class Users(db.Model):
    sno = db.Column( db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)

class Posts(db.Model):
    sno = db.Column( db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    stime = db.Column(db.String(10), nullable=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    


class Contacts(db.Model):
    sno = db.Column( db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(256), nullable=False)
    stime = db.Column(db.String(10), nullable=True)

@app.route('/')
def index():
    posts=Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    #pagination logic
    if(not str(page).isnumeric()):
        page=1
    else:
        page = int(page)
    
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page="+str(page+1)
    elif page == last:
        prev = "?page="+str(page-1)
        next="#"
    else:
        prev = "?page="+str(page-1)
        next = "/?page="+str(page+1)

    pics=[filtering(i.title) for i in posts]
    total={
        "total":len(posts),
        'pics':pics
    }
    return render_template('index.html',posts=posts,params=params,total=total,prev=prev,next=next)


@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')
        mess=Contacts(name=name, msg=msg,phone=phone, email=email, stime=datetime.now())
        db.session.add(mess)
        db.session.commit()
        message = {
            'title':"Success yipppeeeeee",
            'message':"Your message has been sent thank you for visiting us we will be contacting you",
            'color':'green'
        }
        return render_template("message.html", message=message)
    else:
        message = {
            'title':"Access Deneied",
            'message':"You cannot Access this route directly please fill the form and wait for conformation thank you",
            'color':'red'
        }
        return render_template('message.html', message=message)


@app.route('/submitPost', methods=['GET','POST'])
def submitPost():
    if request.method == 'POST':
        username = request.form.get('username')
        password=request.form.get('password')
        title = request.form.get('title')
        description = request.form.get('description')
        user = Users.query.filter_by(username=username).first()
        print(password)
        print(user.password)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                post=Posts(username=username, title=title,description=description,  stime=datetime.now())
                db.session.add(post)
                db.session.commit()
                message = {
            'title':"Success yipppeeeeee",
            'message':"Your post has been uploaded thank you for using our services!",
            'color':'green'
        }
                return render_template("message.html", message=message)
        else:
            message = {
            'title':"Bad Credentials",
            'message':"Your Password or username is incorrect please check and try again",
            'color':'red'
        }
            return render_template('message.html', message=message)
    else:
        message = {
            'title':"Access Deneied",
            'message':"You cannot Access this route directly please fill the form and wait for conformation thank you",
            'color':'red'
            }
        return render_template('message.html',message=message)

@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password=bcrypt.hashpw(request.form.get('password').encode('UTF-8'), bcrypt.gensalt())
        a=Users.query.filter_by(username=username).count()
        if a==0:
            user=Users(name=name, email=email, password=password, username=username)
            db.session.add(user)
            db.session.commit()
            message = {
            'title':"Yippee success!",
            'message':"You are now a member of our blog service thank you for joning. Now You can write posts",
            'color':'green'
                        }
            return render_template('message.html', message=message)
        else: 
            message = {
            'title':"Bad Credentials",
            'message':"Please check the username u entered its already registered choose a new one",
            'color':'red'
        }
            return render_template('message.html', message=message)
    else:
        message = {
            'title':"Access Deneied",
            'message':"You cannot Access this route directly please fill the form and wait for conformation thank you",
            'color':'red'
        }
        return render_template('bad.html', message=message)
        
@app.route('/admin', methods=['GET','POST'])
def adminLogin():
    posts = Posts.query.all()
    contacts = Contacts.query.filter_by().all()
    users = Users.query.filter_by().all()
    print(1)
    if 'user' in session and session['user']==params['username']:
        print(2)
        return render_template("dashboard.html", posts=posts, contacts=contacts, users=users)
    
    uname=request.form.get('uname')
    password=request.form.get('password')
    if uname==params['username'] and password==params['password']:
        session['user']=uname
        print(3)
        return render_template("dashboard.html", posts=posts,contacts=contacts, users=users)
    else:
        print(4)
        message="Welcome to admin panel Please Enter the correct credentials"
        msg = {"msg": message}
        return render_template("login.html", msg=msg)

@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    return redirect('/admin')

@app.route('/deletePost/<string:sno>', methods=['GET','POST'])
def deletePost(sno):
    if 'user' in session and session['user']==params['username']:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/admin')
    else:
        return redirect('/admin')

@app.route('/deleteUser/<string:sno>', methods=['GET','POST'])
def deleteUser(sno):
    print(1)
    if 'user' in session and session['user']==params['username']:
        user=Users.query.filter_by(sno=sno).first()
        db.session.delete(user)
        db.session.commit()
        return redirect('/admin')
    else:
        return redirect('/admin')
@app.route('/deleteMessage/<string:sno>', methods=['GET','POST'])
def deleteMessage(sno):
    if 'user' in session and session['user']==params['username']:
        message=Contacts.query.filter_by(sno=sno).first()
        db.session.delete(message)
        db.session.commit()
        return redirect('/admin')
    else:
        return redirect('/admin')

@app.route('/game')
def game():
    return render_template('game.html')

if __name__ == "__main__":
    app.run(debug=True)
