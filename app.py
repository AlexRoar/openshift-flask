from flask import *
import requests, os

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.secret_key = 'secret_key'
app.run(host='0.0.0.0',port=5000,debug=True)

@app.route('/health')
def f_health():
    return 'OK'

@app.route('/home')
def f_home():
    return 'Hello, Earth!'

@app.route('/')
def f_root():
    return 'Hello, World!'


