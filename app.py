from flask import Flask,render_template,request, session, flash, redirect, url_for,session,logging,request
import sqlite3
import json
import datetime, time
from flask import g
import hashlib
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from data import *
DATABASE = 'database1.db'

app = Flask(__name__)
app.secret_key = "myfirstdbkey"
conn = sqlite3.connect(DATABASE)
c = conn.cursor()
#conn.execute('DROP TABLE USER IF EXIST')
conn.execute('CREATE TABLE IF NOT EXISTS USER (UID INTEGER PRIMARY KEY AUTOINCREMENT,NAME VARCHAR(10) NOT NULL,PASSWORD VARCHAR(100) NOT NULL,EMAIL VARCHAR(50),TYPE INTEGER NOT NULL,ADDRESS VARCHAR(100),BOOKCNT INTEGER DEFAULT 0 )')
conn.execute('CREATE TABLE IF NOT EXISTS AUTHOR (AID INTEGER PRIMARY KEY AUTOINCREMENT,NAME VARCHAR(10) NOT NULL,EMAIL VARCHAR(50),ADDRESS VARCHAR(100) ) ')
conn.execute('CREATE TABLE IF NOT EXISTS PUBLISHER (PID INTEGER PRIMARY KEY AUTOINCREMENT,NAME VARCHAR(10) NOT NULL,EMAIL VARCHAR(50),ADDRESS VARCHAR(100) ) ')
conn.execute('CREATE TABLE IF NOT EXISTS WRITE (BID INTEGER,AID INTEGER,FOREIGN KEY(BID) REFERENCES BOOK(BID),FOREIGN KEY(AID) REFERENCES AUTHOR(AID))')
conn.execute('CREATE TABLE IF NOT EXISTS BOOK (BID INTEGER PRIMARY KEY AUTOINCREMENT,TITLE VARCHAR(30) NOT NULL,LANGUAGE VARCHAR(10) NOT NULL,TYPE VARCHAR(20) NOT NULL,SHELF_NO INTEGER(5) NOT NULL,ATID INTEGER NOT NULL,PBID INTEGER NOT NULL,FOREIGN KEY(ATID) REFERENCES AUTHOR(AID),FOREIGN KEY(PBID) REFERENCES PUBLISHER(PID) )')
conn.execute('CREATE TABLE IF NOT EXISTS BORROWS (TID INTEGER PRIMARY KEY AUTOINCREMENT,UID INTEGER NOT NULL ,BID INTEGER NOT NULL,DUE_MONEY INTEGER(1000),ADDRESS VARCHAR(100),FOREIGN KEY(UID) REFERENCES USER(UID),FOREIGN KEY(BID) REFERENCES BOOK(BID) ) ')
# c.execute('SELECT * FROM blog;')


conn.commit()
print(c.fetchone())
conn.close()

article = Articles()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

class FRB(Form):
    BOOKID = StringField('BOOKID',[validators.DataRequired()])
    UID = StringField('UID',[validators.DataRequired()])

@app.route('/frb',methods=['GET','POST'])
def frb():
    form3 = FRB(request.form)
    if session.get('loggedin')==False:
        return "<script>alert('you are already logged in');window.location='/login'</script>"
    else:
        return render_template('frb.html',form=form3)

@app.route('/articles')
def articles():
    return render_template('articles.html',articles = article)

@app.route('/articles/<string:id>/')
def singlearticle(id):
    return render_template('singlearticle.html',id = id,articles = article)

class RegisterForm(Form):
    NAME = StringField('NAME',[validators.Length(min=1,max=20),validators.DataRequired()])
    EMAIL = StringField('EMAIL',[validators.Length(min=1,max=29)])
    PASSWORD =PasswordField('PASSWORD',[
    validators.DataRequired(),
    validators.EqualTo('CONFIRM',message='Passwords do not match')
    ])
    print("aaaaa")
    ADDRESS = StringField('ADDRESS',[validators.Length(min=1,max=100)])
    TYPE = StringField('TYPE',[validators.AnyOf(['1','2','3'])])
    CONFIRM = PasswordField('CONFIRM')

class LoginForm(Form):
    NAME = StringField('NAME',[validators.Length(min=1,max=20),validators.DataRequired()])
    PASSWORD=PasswordField('PASSWORD',[
    validators.DataRequired(),
    validators.EqualTo('CONFIRM',message='Passwords do not match')
    ])

@app.route('/register',methods=['GET','POST'])
def register():
    if session.get('loggedin'):
        return "<script>alert('you are already logged in');window.location='/'</script>"
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with sqlite3.connect(DATABASE) as conn:
            cur=conn.cursor()
            NAME = request.form['NAME']
            PASSWORD = request.form['PASSWORD']
            EMAIL = request.form['EMAIL']
            SALT = '777'
            actualP = PASSWORD+SALT
            h = hashlib.md5(actualP.encode())
            ADDRESS = request.form['ADDRESS']
            TYPE = request.form['TYPE']
            data = cur.execute('SELECT * FROM USER WHERE NAME=? OR PASSWORD=?;',(NAME,h.hexdigest()))
            data=cur.fetchall()
            if len(data)>0:
                    flash('Name or password already registered')
                    return render_template('register.html',form=form)
            else:
                    cur.execute('INSERT INTO USER(NAME,PASSWORD,EMAIL,TYPE,ADDRESS) VALUES(?,?,?,?,?);',(NAME,h.hexdigest(),EMAIL,int(TYPE),ADDRESS))
                    conn.commit()
                    print("dhvanil")
                    return "Yeah You registerend successfull"
                    conn.close()
    else:
        return render_template('register.html',form = form)

@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('loggedin'):
        return "<script>alert('You are already loggedin');window.location='/'</script>"
    else:
        form2= LoginForm(request.form)
        if request.method =='POST':
            with sqlite3.connect(DATABASE) as conn:
                cur1 = conn.cursor()
                NAME = request.form['NAME']
                PASSWORD = request.form['PASSWORD']
                SALT = '777'
                actualP = PASSWORD+SALT
                h = hashlib.md5(actualP.encode())
                data = cur1.execute('SELECT * FROM USER WHERE NAME=? and PASSWORD = ?;',(NAME,h.hexdigest()))
                data = cur1.fetchall()
                if len(data)>0:
                    session['loggedin']=True
                    session['name']=NAME
                    flash('You are successfully logged in')
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html',form=form2)
        else:
            return render_template('login.html',form = form2)

if __name__ == '__main__':
    app.run(port=5001,debug = True)
