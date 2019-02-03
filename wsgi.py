from flask import Flask, flash, request,render_template, redirect, url_for, session, make_response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
import random
import os
################# initialize flask ####################################
application = Flask(__name__)
################## application config ###################################
application.config['MONGO_DBNAME'] ='applee'
application.config['MONGO_URI'] = 'mongodb://elvischuks:123elvischuks@mongodb:27017/applee'

#application.config['MONGO_DBNAME'] = 'apply'
#application.config['MONGO_URI'] = 'mongodb://elvis:elvischuks@127.0.0.1:27017/apply'
application.secret_key = "superisasecretisakey"
################# initialize pymongo ####################################
mongo = PyMongo(application)
upload = os.getcwd()
upload_folder = upload + '/static/icon'
pro_fold = upload + '/static/profile'


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
def index():
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
################################ login route ##########################
@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users
        check = user.find_one({'email':request.form['email']})
        if check:
            if check_password_hash(pwhash=check['password'], password=request.form['password']):
                session['email'] = request.form['email']
                return redirect(url_for('dashboard'))
            flash('incorrect password and email combo')
    return render_template('login.html')
@application.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = session['email']
        app = mongo.db.apps
        message = mongo.db.messages
        check = app.find({'email':user})
        users = mongo.db.users
        checku = users.find_one({'email':user})
        checkm = message.find_one({'email':user})
        if checkm:
            text = checkm['text']
            render_template('dashboard.html', text=text)
        if checku:
            fin = checku['profile']
            render_template('dashboard.html', fin=fin)
        elif checku is None:
            fin = ''
            pass
        found = (doc for doc in check)
        return render_template('dashboard.html', user=user, found=found, fin=fin)
    return redirect(url_for('login'))


@application.route('/dashboard/create', methods=['GET', 'POST'])
def create():
    if 'email' in session:
        user = session['email']
        app = mongo.db.apps
        if request.method == 'POST':
            url = request.form['url']
            name = request.form['appname']
            import pprint
            from apiclient.discovery import build
            import socket
            #make api call to googles urlTestingTools
            API_KEY = 'AIzaSyACKc0SQ80qbBwgVnJUaBq_XVrmRHr8Ymw'
            service = build('searchconsole', 'v1', developerKey=API_KEY)
            params = {
                  'url':url,
                  'requestScreenshot':True,
                  }
            req = service.urlTestingTools().mobileFriendlyTest().run(body=params, x__xgafv=None)
            try:
                response = req.execute()
                if response['mobileFriendliness'] == 'MOBILE_FRIENDLY':
                    from PIL import Image
                    from io import BytesIO
                    import base64
                    imgdata = response['screenshot']['data']
                    #save image
                    im = Image.open(BytesIO(base64.b64decode(imgdata)))
                    im.save('static/screenshots/'+ name +'.png')
                    img = name +'.png'
                    #########
                    check = app.find_one({'appname':name})

                    if check is None:
                        app.insert({
                        'email':session['email'],
                        'appname':name,
                        'url':url,
                        'img': img
                        })
                        session['img'] = img
                        return redirect(url_for('createnext'))

                    return 'app already exists'
                return 'Sorry this website is not Mobile friendly'
            except socket.timeout:
                return 'there appears to be a problem at the moment, please try again later'
        return render_template('create.html', user=user)
    return redirect(url_for('login'))
@application.route('/createnext')
def createnext():
    img = session['img']
    return render_template('createnext.html',img=img)

@application.route('/dashboard/final', methods=['GET','POST'])
def final():
    if 'email' in session:
        user = mongo.db.users
        app = mongo.db.apps
        img = session['img']
        if request.method == 'POST':
            check = app.find_one({'img':img})
            if check:
                ver = request.form['version']
                plat = request.form['platform']
                pric = request.form['pricing']

                app.update({'img':check['img']}, {'$set':{'version':ver,'platform':plat,'pricing':pric,'icon':img}})
                message = mongo.db.messages
                message.insert({'email':session['email'],
                'text':'Your app is being created and will be uploaded to the app stores shortly'})
                f = request.files['icon']
                filena = secure_filename(img)
                f.save(os.path.join(upload_folder,filena))
                #os.path.join(app.config['UPLOAD_FOLDER'],
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                fromaddr = "appleeweb@gmail.com"
                toaddr = session['email']
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "Applee support"
                username = session['email']
                body =  "Hello {} ".format(username)
                html = """\
                    <html>
                    <head></head>
                    <body>
                    <h2>Hello from the Applee team</h2>
                    <p>Thank you for deciding to use App-Lee </br>
                    Your app is being created and will be uploaded to the app store,</br>
                    kindly sit back and enjoy our services.</br>
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

                #msg.attach(MIMEText(body, 'plain'))
                import smtplib
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.ehlo()
                s.starttls()
                s.login("appleeweb@gmail.com", "@123Applee")
                text = msg.as_string()
                s.sendmail(fromaddr, toaddr, text)
                s.quit()

                return redirect(url_for('dashboard'))

        return render_template('final.html')
    return redirect(url_for('login'))

@application.route('/dashboard/apps/<path:app>')
def apps(app):
    if 'email' in session:
        appi = mongo.db.apps
        check = appi.find_one({'appname': app })
        appname = check['appname']
        version = check['version']
        plat = check['platform']
        url = check['url']
        img = check['img']
        price = check['pricing']
        user = session['email']
        return render_template('apps.html', appname=appname, img=img,
        version=version,plat=plat,url=url,price=price, user=user )
    return redirect(url_for('login'))

@application.route('/dashboard/profile', methods=['GET','POST'])
def profile():
    if 'email' in session:
        user = session['email']
        prof = mongo.db.users
        check = prof.find_one({'email': user})
        email = check['email']
        username = check['username']
        fin = email[2:7] +'.png'
        if request.method == 'POST':
            f = request.files['photo']
            f.save(os.path.join(pro_fold,fin))
            prof.update({'email':email}, {'$set':{'profile':fin, 'username':request.form['username']}})
            flash('profile updated')
        return render_template('profile.html', user=user, email=email, username=username, fin=fin)
    return redirect(url_for('login'))

@application.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        comments = request.form['comments']
        #### email logic #########
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        fromaddr = "appleeweb@gmail.com"
        toaddr = "appleeweb@gmail.com"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Customer message"
        username = name
        body =  "Hello awsome apple support staff this message came from {}, email : {}, comments : {} ".format(name,email,comments)
        html = """
            <html>
            <head></head>
            <body>
            <h2>Customer email</h2>

               </body>
               </html>
               """
        part1 = MIMEText(body,'plain')
        part2 = MIMEText(html,'html')

        msg.attach(part1)
        msg.attach(part2)

        #msg.attach(MIMEText(body, 'plain'))
        import smtplib
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.login("appleeweb@gmail.com", "@123Applee")
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        flash('comment sent, we would get back to you shortly')
    return redirect(url_for('index'))
############################################################################################
@application.route('/clearpassword=elvis')
def clear():
    app = mongo.db.apps
    app.drop()
    return 'db cleared'

@application.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
@application.route('/logout')
def logout():
    if 'email'in session:
        session.pop('email', None)
        return redirect(url_for('login'))
    return redirect(url_for('index'))
if __name__ == "__main__":
    application.run(debug=True)
