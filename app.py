from flask import *
import requests, os

app = Flask(__name__)
# app.secret_key = 'secret_key'

@app.route('/health')
def f_health():
    return 'OK'

# @app.route('/home')
# def f_home():
#     return '<h1>Hello, Earth!</h1>'

@app.route('/')
def f_root():
    # return '<h1>Hello, World!</h1> <p> This container hostname is: {}</p>'.format(os.environ['HOSTNAME'])
    return '<h1>Hello, World!</h1> <p> We are in <b>{}</b></p> <p> This container hostname is: {}</p>'.format(os.environ['STAGE'],os.environ['HOSTNAME'])

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
