from flask import *
import requests, os

app = Flask(__name__)
# app.secret_key = 'secret_key'

@app.route('/health')
def f_health():
    return 'OK'

@app.route('/home')
def f_home():
    return 'Hello, Earth!'

@app.route('/')
def f_root():
    return 'Hello, World!\n This container hostname is: {}'.format(os.environ['HOSTNAME'])

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
