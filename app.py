from flask import *
import requests, os

app = Flask(__name__)
# app.secret_key = 'secret_key'
# app.run(host='0.0.0.0',port=5000,debug=True)

@app.route('/health')
def f_health():
    return 'OK'

@app.route('/home')
def f_home():
    return 'Hello, Earth!'

@app.route('/')
def f_root():
    return 'Hello, World!'

@app.route('/empty-view/')
def empty_view(self):
    content = {'please move along': 'nothing to see here'}
    return content, status.HTTP_404_NOT_FOUND
