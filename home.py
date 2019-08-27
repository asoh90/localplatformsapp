#!/usr/bin/python

from flask import Flask, render_template, url_for, flash, redirect, request, send_file, session
from flask_oauth import OAuth
from forms import SelectPlatformForm, SelectFunctionForm
from werkzeug.utils import secure_filename
import variables
import platform_manager as pm
import os
import random, threading, webbrowser
import sys
import datetime
import logging
from logging.handlers import RotatingFileHandler
from urllib.request import Request, urlopen, URLError
import json
from functools import wraps

# Google SSO Credentials
GOOGLE_CLIENT_ID = '696774976262-rg17k58uiani498vqkjdekfdunh7c6j3.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'ceM7QWDLzwA-7xJ0qalIPweP'
REDIRECT_URI = "/oauth2callback"
DEBUG = True

app = Flask(__name__)
# app.debug = DEBUG
oauth = OAuth()

app.config['SECRET_KEY'] = variables.SECRET_KEY
app.config["UPLOAD_FOLDER"] = variables.UPLOAD_FOLDER
RETURN_FOLDER = variables.RETURN_FOLDER
UPLOAD_FOLDER = variables.UPLOAD_FOLDER

# access token by default expires in 1 hour: https://stackoverflow.com/questions/13851157/oauth2-and-google-api-access-token-expiration-time
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

def authenticate(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # access_token = session.get('access_token')
        # # print("ACCESS TOKEN: {}".format(access_token))
        # if access_token is None:
        #     return redirect(url_for('login'))
        # access_token = access_token[0]
        
        # headers = {'Authorization': 'OAuth '+ access_token}
        # req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
        #             None, headers)
        # try:
        #     res = urlopen(req)
        # except URLError as e:
        #     if e.code == 401:
        #         # Unauthorized - bad token
        #         session.pop('access_token', None)
        #         return redirect(url_for('login'))

        # login_response = res.read().decode('utf-8')
        # login_dict = json.loads(login_response)
        # session["email"] = login_dict["email"]

        check_output = check_login()
        # if check_output == None:
        #     return redirect(url_for('home'))
        # else:
        #     return check_output
        if not check_output is None:
            return check_output
        else:
            return f(*args, **kwargs)
    return wrap

@app.route("/")
def index():
    return redirect(url_for('home'))

def check_login():
    access_token = session.get('access_token')
    # print("check_login ACCESS TOKEN: {}".format(access_token))
    if access_token is None:
        return redirect(url_for('login'))
    access_token = access_token[0]
    
    headers = {'Authorization': 'OAuth '+ access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))

    login_response = res.read().decode('utf-8')
    login_dict = json.loads(login_response)
    session["email"] = login_dict["email"]
    return None
 
@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route("/home", methods=['GET','POST'])
@authenticate
def home():
    # delete all files in upload and to_return folders
    delete_upload_and_to_return_files()
    credentials = app.config.get('credentials')
    if credentials == None:
        render_template('error.html')
    
    variables.read_credentials(credentials)

    form = SelectPlatformForm()
    # if form.validate_on_submit():
    #     return redirect(url_for("function", platform=form.platform.data))
    platform_functions = variables.get_platform_functions(session["email"])
    return render_template('home.html', form=form, platform_functions=platform_functions)


# Test page
# @app.route("/testhome", methods=['GET','POST'])
# def testhome():
#     return render_template('testhome.html')

# when file gets dropped into the dropzone, or "Query" function is selected, run this
@app.route("/process", methods=['GET','POST'])
@authenticate
def process():
    # get fields
    platform = request.form['platform']
    function = request.form['function']
    save_path = None

    if not "Query" in function:
        # Get downloaded file
        fileob = request.files["file"]
        filename = secure_filename(fileob.filename)
        save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], filename)
        fileob.save(save_path)

    output = pm.callAPI(platform, function, save_path)
    # print(output)

    # Returns file if no error message
    try:
        output_file = output["file"]
        response = send_file(RETURN_FOLDER + "/" + output_file, as_attachment=True, attachment_filename=output_file)
        response.headers['message'] = output["message"]
        return response
    # If no file is returned, error message is returned instead
    except:
        return output["message"]

@app.route("/downloaduploadtemplate", methods=['GET','POST'])
@authenticate
def download_upload_template():
    return send_file("UploadTemplate.xlsx", as_attachment=True, attachment_filename="UploadTemplate.xlsx")

@app.route("/test", methods=['GET','POST'])
def test():
    print("I AM IN TEST")
    # return send_file(RETURN_FOLDER + "The_Trade_Desk_2018-08-28_21;51;47.xlsx", as_attachment=True, attachment_filename="The_Trade_Desk_2018-08-28_21;51;47.xlsx")

# ------------------------------- Non route functions -----------------------------------------
def delete_upload_and_to_return_files():
    return_filelist = [return_file for return_file in os.listdir(RETURN_FOLDER) if return_file.endswith(".xlsx")]
    for return_file in return_filelist:
        os.remove(os.path.join(RETURN_FOLDER, return_file))

try:
    if __name__ == "__main__":
        variables.logger = logging.getLogger('my_logger')
        handler = RotatingFileHandler('logs/my_log.txt', maxBytes=10000000000, backupCount=9999)
        variables.logger.addHandler(handler)

        print("System is running")
        app.config['credentials'] = sys.argv[1]
        port = 5000
        url = "http://127.0.0.1:{0}".format(port)
        threading.Timer(1.25, lambda: webbrowser.open(url)).start()
        app.run(threaded=True, host='0.0.0.0')
except Exception as ex:
    variables.logger.warning("{} {}".format(datetime.datetime.now().isoformat(), ex))
    # print(ex)

# Test function
# @app.route("/function", methods=['GET','POST'])
# def function():
#     platform_selected = {'name':request.args['platform']}
#     print("Platform Selected: " + platform_selected['name'])

#     form = SelectFunctionForm()
#     return render_template('function.html', title="Select Function", platform=platform_selected)
