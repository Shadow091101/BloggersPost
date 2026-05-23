from flask import Flask,render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
import pymysql
from datetime import datetime
import json
import os

app=Flask(__name__)

with open("config.json","r") as c:
    config=json.load(c)
    
params = config["params"]
mail_params = config["mail_params"]

app.config['MAIL_SERVER']=mail_params['mail_server']
app.config['MAIL_PORT']=mail_params['mail_port']
app.config['MAIL_USE_TLS']=mail_params['mail_use_tls']
app.config['MAIL_USERNAME']=mail_params['mail_username']
app.config['MAIL_PASSWORD']=mail_params['mail_password']
app.config['MAIL_DEFAULT_SENDER']=mail_params['mail_default_sender']

mail=Mail(app)

local_server = os.environ.get("LOCAL_SERVER", params.get("local_server")) == "True"

pymysql.install_as_MySQLdb()
if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)

class Contact(db.Model): 
    #this would create a model for the table
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    msg = db.Column(db.String (120), unique=False, nullable=False)
    date = db.Column(db.String (100),nullable=True)
    
class Posts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    content = db.Column(db.String(150), unique=False, nullable=False)
    author = db.Column(db.String (120), unique=False, nullable=False)
    slug=db.Column(db.String(100),unique=False,nullable=False)
    date = db.Column(db.DateTime,nullable=True)
    

@app.route("/")
def index():
    posts = Posts.query.order_by(Posts.date.desc()).limit(3).all()
    return render_template("index.html", params=params, posts=posts,active="home")

@app.route("/posts")
def all_posts():
    posts = Posts.query.order_by(Posts.date.desc()).all()
    return render_template("all_posts.html", params=params, posts=posts,active="posts")

@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")

@app.route("/posts/<string:post_slug>",methods=['GET'])

def posts(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('posts.html',params=params,post=post,active="posts")

@app.route("/contact",methods=['GET','POST'])

def contact():
    if(request.method=='POST'):
        
        '''Add entry to the database'''
        name=request.form.get('name')
        email=request.form.get('email')
        msg=request.form.get('msg')
        
        entry=Contact(name=name, email=email, msg=msg, date=datetime.now()) # here first one is from db and second one is the instance that we fetch from form
        
        db.session.add(entry)
        db.session.commit()
        
        message=Message(
            subject=f"New message from {name}",
            recipients=[app.config['MAIL_USERNAME']]
        )
        
        message.reply_to=email
        message.body=f"""
        
        Name:{name}
        Email:{email}
        
        Message:{msg}
        """
        mail.send(message)
    return render_template('contact.html',params=params,active="contact")

if __name__=="__main__":
    app.run(debug=True)#Whenever we make changes in code and save it gets reflected in real-time due to use of debug=True