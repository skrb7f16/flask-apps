from flask import Flask,render_template,request,redirect,url_for,flash
from wtformsfields import *
from flask_sqlalchemy import SQLAlchemy
from models import *
from flask_login import LoginManager,login_user,current_user,login_required, logout_user
from flask_socketio import SocketIO ,send,emit,join_room,leave_room
from time import localtime,strftime

app=Flask(__name__)



app.secret_key ="replace later"


#configuere database
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/rchat'

db=SQLAlchemy(app)
# initialize socketio
socketio=SocketIO(app)

ROOMS = ['lounge','news','games','coding']

# initialisation of login
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route('/', methods=['GET','POST'])
def index():

    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username=reg_form.username.data
        password=reg_form.password.data
        hashedPwd=pbkdf2_sha256.hash(password)
        user=Users(username=username,password=hashedPwd)
        db.session.add(user)
        db.session.commit()
        flash("User Registered",category="success")
        return redirect(url_for('login'))

    return render_template('index.html', form=reg_form)


@app.route("/login",methods=["GET","POST"])
def login():
    login_form = LoginForm()
    
    # allowing only after validaters
    if login_form.validate_on_submit():
        user_obj=Users.query.filter_by(username=login_form.username.data).first()
        login_user(user_obj)
        return redirect(url_for('chat')) 
    
    return render_template("login.html",form=login_form)


@app.route('/chat',methods=["GET","POST"])
def chat():
    if not current_user.is_authenticated:
        flash("Please Login Before Accessing",category='danger')
        return redirect(url_for('login'))
    return render_template('chat.html',username=current_user.username,rooms=ROOMS)


@app.route('/logout',methods=["GET"])
def logout():
    logout_user()
    flash("User Logout",category="success") 
    return redirect(url_for('login'))

@socketio.on('message')
def message(data):
    send({'msg':data['msg'],'username':data['username'],'time_stamp':strftime('%a, %d %b %I:%M%p',localtime()) },room=data['room'])

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg':data['username']+" has joined the "+data['room']+" room"}, room=data['room'])

@socketio.on('leave')
def join(data):
    leave_room(data['room'])
    send({'msg':data['username']+" has left the "+data['room']+" room"},room=data['room'])

if __name__ == "__main__":
    socketio.run(app,debug=True) 