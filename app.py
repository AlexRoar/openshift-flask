"""
Importing os and Flask modules
"""
import os
from flask import Flask

APP = Flask(__name__)
# APP.secret_key = 'secret_key'


@APP.route('/health')
def f_health():
    """
    Health Check for the Flask app
    """
    return 'OK'

# @APP.route('/home')
# def f_home():
#     return '<h1>Hello, Earth!</h1>'


@APP.route('/')
def f_root():
    """
    Welcome page
    """

    return """
    <h1>Hello, World!</h1>
    <p> This container hostname is: {}</p>
    """.format(os.environ['HOSTNAME'])
    # return """
    # <h1>Hello, World!</h1>
    # <p> We are in <b>{}</b></p>
    # <p> This container hostname is: {}</p>
    # """.format(os.environ['STAGE'],os.environ['HOSTNAME'])


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
