from flask import Flask
from flask_pymongo import PyMongo


application = Flask(__name__)

application.config['MONGO_DBNAME'] ='applee'
application.config['MONGO_URI'] = 'mongodb://elvischuks:123elvischuks@127.0.0.1:27017/applee'
application.secret_key = "superisasecretisakey"
mongo = PyMongo(application)



@application.route("/")
def hello():
    e = mongo.db.apps
    apps.insert({'name':'test'})
    return 'hey this is applee'

@application.route("/test")
def test():
    import pprint
    from apiclient.discovery import build
    import socket
            #make api call to googles urlTestingTools
    API_KEY = 'AIzaSyACKc0SQ80qbBwgVnJUaBq_XVrmRHr8Ymw'
    service = build('searchconsole', 'v1', developerKey=API_KEY)
    url = 'https://google.com'
    params = {
                'url':url,
                'requestScreenshot':True,
                }
    req = service.urlTestingTools().mobileFriendlyTest().run(body=params, x__xgafv=None)
    try:
        response = req.execute()
        if response['mobileFriendliness'] == 'MOBILE_FRIENDLY':
            return 'mobile friendly'
    except socket.timeout:
        return 'there appears to be a problem at the moment, please try again later'
@application.route("/mail")
def mail():
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    fromaddr = "appleeweb@gmail.com"
    toaddr = "celvischuks@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Applee support"
    username = 'elvis'
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
    return 'mail works'


if __name__ == "__main__":
    application.run()
