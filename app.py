# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals
import os
from flask import Flask
from modules_alice.paronims import paronims
from modules_alice.stress import stress
from modules_alice.quotes import quotes
from modules_alice.elephant import elephant


import logging
APP = Flask(__name__)
# APP.secret_key = 'secret_key'
logging.basicConfig(level=logging.DEBUG)

APP.register_blueprint(elephant)  # Другое решение
APP.register_blueprint(quotes)  # Другое решение
APP.register_blueprint(paronims)  # Наше, отобранное решение
APP.register_blueprint(stress)

@APP.route('/health')
def f_health():
    """
    Health Check for the Flask app
    """
    return 'OK'

@APP.route("/", methods=['POST', 'GET'])
def main():
    return 'School 1581 skills router'


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
