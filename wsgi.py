from flask import Flask, flash, request,render_template, redirect, url_for, session, make_response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import random
import os
################# initialize flask ####################################
application = Flask(__name__)
################## application config ###################################
application.config['MONGO_DBNAME'] ='applee'
application.config['MONGO_URI'] = 'mongodb://elvischuks:123elvischuks@mongodb:27017/applee'
application.secret_key = "superisasecretisakey"
################# initialize pymongo ####################################
mongo = PyMongo(application)
@application.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
    ######## Cache clearer ############################

################# routes ####################################
@application.route("/")
def hello():
    return render_template('index.html')
@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = mongo.db.users
        check = user.find_one({'email':request.form['email']})
        if check is None:
            import secrets
            token = secrets.token_urlsafe()
            user.insert({
            'email':request.form['email'],
            'username':request.form['username'],
            'token':token,
            'password':False,
            'free':True,
            'paid':False
            })
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            fromaddr = "appleeweb@gmail.com"
            toaddr = request.form['email']
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Applee Registration"
            url = "http://app-lee-app-lee.1d35.starter-us-east-1.openshiftapps.com/confirm/"
            fin = url + token
            username = request.form['username']
            body = "Hello {}, \nyour email confirmation link : {} ".format(username, fin)
            html = """\
                <html>
                <head></head>
                <body>
                <h2>Hello from the Applee team</h2>
                <p>Thank you for deciding to use App-Lee </br>
                Follow the link above to confirm your email address and get access to your dashboard,</br>
                Reply this mail if you experience difficulties.</br>
                </p>
                <style>
                h2{
                   color:red;
                   }
                   </style>
                   </body>
                   </html>
                   """
            part1 = MIMEText(body,'plain')
            part2 = MIMEText(html,'html')

            msg.attach(part1)
            msg.attach(part2)
            import smtplib
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.ehlo()
            s.starttls()
            s.login("appleeweb@gmail.com", "@123Applee")
            text = msg.as_string()
            s.sendmail(fromaddr, toaddr, text)
            s.quit()
            return redirect(url_for('waiting'))
        flash('user already exists')

    return render_template('register.html')
@application.route('/checkmail')
def waiting():
    return render_template('waiting.html')
@application.route('/confirm/<path:token>', methods=['GET', 'POST'])
def confirm(token):
    toke = token
    if request.method == 'POST':
        user = mongo.db.users
        check = user.find_one({'token':token})
        if check is None:
            return ' this link has expired'
        if request.form['password'] == request.form['repass']:
            password = generate_password_hash(request.form['password'])
            user.update({'token':check['token']},{'$set':{'password':password}})
            session['email'] = check['email']
            return redirect(url_for('dashboard'))
        flash('passwords do not match')
    return render_template('confirm.html', toke=toke)
@application.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = session['email']
        app = mongo.db.apps
        check = app.find({'email':user})
        found = (doc for doc in check)
        return render_template('dashboard.html', user=user, found=found)
    return redirect(url_for('login'))


if __name__ == "__main__":
    application.run()
