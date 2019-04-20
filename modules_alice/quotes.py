# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Blueprint, request
import json
import logging
from random import randint
import os

quotes = Blueprint('quotes', __name__)

# Get quotes base
base = open(os.path.dirname(os.path.abspath(__file__))+'/data/quotes/cit.json', 'r', encoding="utf-8")
data = json.loads(base.read())
base.close()

sessionStorage = {}  # Sessions storage


@quotes.route('/quotes', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    response = handle(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def handle(req, res):
    user_id = req['session']['user_id']
    res['response']['buttons'] = [{
        "title": "Еще",
        "hide": True
    }]
    if req['session']['new'] or user_id not in sessionStorage.keys():
        # New user
        sessionStorage[user_id] = {'suggests': []}
        res['response']['text'] = 'Привет! Я отправляю пацанские цитаты на все случаи жизни. Раскажи мне что-нибуть.'
        return res

    # Get quote
    if (req['request']['original_utterance'].lower() == 'еще'):
        res['response']['text'] = get_response("asdfghjk_рандомная_строка_которой_точно_нет", data)
    else:
        res['response']['text'] = get_response(req['request']['original_utterance'].lower(), data)

    return res


def get_response(rqst, data):  # получение ответа
    rqst = rqst.split()  # Get words
    response_number = (randint(0, len(data) - 1))  # Random position
    found = False
    start = randint(0, (len(data) - 1) // 2)  # Random start position
    for word in rqst:
        if found: break
        for number in range(start, len(data) + start):
            if found: break
            if number >= len(data): number -= len(data)  # Overflow check
            tmp = data[number].split()
            for i in tmp:
                if i.lower() == word.lower():
                    # print(i, word)
                    found = True
                    response_number = number
                    break
    return data[response_number]
