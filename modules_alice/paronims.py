from flask import Blueprint, request
import json
import logging
import random
import os

import sqlite3

paronims = Blueprint('paronims', __name__)

data = open(os.path.dirname(os.path.abspath(__file__))+'/data/paronims/paronimsNew.json', 'r', encoding="utf-8")
base = json.loads(data.read())
data.close()

connection = sqlite3.connect('database.db')
c = connection.cursor()

sessionStorage = {}  # Sessions storage


@paronims.route('/paronims', methods=['POST'])
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
    if req['session']['new'] or user_id not in sessionStorage.keys():
        # New user
        sessionStorage[user_id] = {'suggests': []}
        res['response']['text'] = 'Привет! Я помогу тебе понять, что какой пароним значит!'
        res['response']['buttons'] = get_suggests(user_id)
        if req['request']['original_utterance'].lower() != 'ping':
            addView()
        return res

    if req['request']['original_utterance'].lower() == 'stat_31415926':
        res['response']['text'] = 'Просмотров:' + str(getViews())
        return res

    posibleBegin = ['Смотрите, что я нашла:', 'Нашла:', 'Кажется, есть:', 'Получилось!', 'Готово.', 'Есть!',
                    'Ура, нашла!', 'Да, такое есть у меня:', 'Смотрите, как все просто:', 'Интересный попался:',
                    'Однако, есть!', 'Ой, как интересно:', 'Да, я нашла.']

    posibleBadBegin = ['Кажется, в русском языке такого нет. Ну, ничего. Скоро придумаем!',
                       'Не нашла, наверное плохо искала... Или его просто нет.',
                       'Не могу найти такой пароним в русском языке, позову маму. Она всегда все находит.',
                       'Интересно... не нашла такого.',
                       'Ой, такого еще не придумали! Правильно, что вы на шаг впереди.']

    index = findByWord(base, req['request']['original_utterance'].lower())  # Search in base

    if index == -1:
        # Not found such paronim
        res['response']['buttons'] = get_suggests(user_id)
        res['response']['text'] = posibleBadBegin[random.randint(0, len(
            posibleBadBegin) - 1)] + ' Проверьте правописание и попробуйте еще раз или выберите какой-нибудь пароним ниже!'
        return res

    res['response']['buttons'] = get_suggests(user_id, index)  # Get suggests with founded word

    res['response']['text'] = posibleBegin[random.randint(0, len(posibleBegin) - 1)]

    tmp = base[index]['inpair'].copy()
    tmp.insert(0, index)

    for par in tmp:
        res['response']['text'] += "\n\r\t ---- " + str(par) + "\n\r"
        if not (base[par]['mention'] == ''):
            res['response']['text'] += base[par]['mention']
            res['response']['text'] += '\n\r'
        if (len(res['response']['text']) >= 1010):
            res['response']['text'] += '...'
            break
        if (len(base[par]['examples']) != 0):
            res['response']['text'] += 'Примеры: ' + '\n\r'
            n = 0
            for i in base[par]['examples']:
                n += 1
                if (len(res['response']['text']) >= 1010):
                    res['response']['text'] += '...'
                    break

                res['response']['text'] += str(n) + ') ' + i.lstrip('1 2 3 4 5 6 7 8 9 0 ) . -') + '\n\r'
            if (len(res['response']['text']) >= 1010):
                break
        if (len(res['response']['text']) >= 1010):
            break
        if (base[par]['popular'] != ''):
            res['response']['text'] += 'Фраза: ' + base[par]['popular'] + '\n\r'

    if (base[index]['reference'] != [] and len(res['response']['text']) < 900):
        res['response']['text'] += "\n\n Данная группа также включает в себя: " + ", ".join(base[index]['reference'])

    if (len(res['response']['text']) >= 1020):
        res['response']['text'] = res['response']['text'][0:1020] + '...'
    return res


def get_suggests(user_id, wordSelected=-1, n=3):
    session = sessionStorage[user_id]  # local user suggests
    suggests = []

    # If concrete word is defined
    if (wordSelected != -1):
        for i in base[wordSelected]['reference']:
            suggests.append({
                "title": i,
                "hide": True
            })

    # set of indexes of already suggested words
    alreadySuggested = set(session['suggests'])

    # generate not seen indexes set and shuffle it
    notSeenIndexes = base.keys()

    # Remove already suggested
    notSeenIndexes = set(notSeenIndexes) - alreadySuggested

    if len(notSeenIndexes) < n:
        # if we already suggested all words
        alreadySuggested = set()

    notSeenIndexes = list(notSeenIndexes)  # Convert to list
    random.shuffle(notSeenIndexes)

    notSeenIndexes = notSeenIndexes[:n]  # n words in suggest

    for i in notSeenIndexes:
        alreadySuggested.add(i)  # Now it becomes suggested
        suggests.append({
            "title": i,
            "hide": True
        })

    session['suggests'] = list(alreadySuggested)  # Update local copy of suggests

    sessionStorage[user_id] = session  # Save changes to global sessionStorage

    return suggests


# Find index of paronims dictionary in base
# a - base with paronims
# search - search word
def findByWord(a, search):
    for i in search.split():
        if i in a.keys():
            return i
    return -1


def addView(name='paronims'):
    res = c.execute('SELECT * FROM `visits_count` WHERE `name`="' + name + '"')
    fetch = res.fetchall()
    if (len(fetch) == 0):
        c.execute('INSERT INTO `visits_count` VALUES ("' + name + '", 1)')
        connection.commit()
        return
    res = fetch[0]
    count = int(res[-1]) + 1
    c.execute("UPDATE `visits_count` SET 'count'=" + str(count) + ' WHERE `name`="' + name + '"')
    connection.commit()


def getViews(name='paronims'):
    res = c.execute('SELECT * FROM `visits_count` WHERE `name`="' + name + '"')
    fetch = res.fetchall()
    if (len(fetch) == 0):
        return 0
    res = fetch[0]
    count = int(res[-1])
    return count
