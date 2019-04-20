# coding=utf-8
from flask import Blueprint, request
import json
import requests
import logging
import random
from urllib.parse import quote, urlsplit, urlunsplit
import urllib.request
from bs4 import BeautifulSoup
import ssl
from lxml.html import fromstring
import string
from urllib import request as urlrequest
import sqlite3

ssl.match_hostname = lambda cert, hostname: True



# For every user:
#
# current action 'action'
# suggestions [word, word] 'sugg'
# correct one 'right'
# already asked [asked words] 'asked'
#

sessionStorage = {}  # Хранилице сессий

winSounds = [
    '<speaker audio="alice-music-tambourine-80bpm-1.opus">',
    '<speaker audio="alice-music-harp-1.opus">',
    '<speaker audio="alice-sounds-things-sword-1.opus">',
    '<speaker audio="alice-sounds-things-bell-1.opus">',
    '<speaker audio="alice-sounds-game-win-1.opus">',
    '<speaker audio="alice-sounds-game-win-2.opus">',
    '<speaker audio="alice-sounds-game-win-3.opus">',
    '<speaker audio="alice-sounds-game-powerup-2.opus">'
]

failSounds = [
    '<speaker audio="alice-music-drums-1.opus">',
    '<speaker audio="alice-music-drums-1.opus">',
    '<speaker audio="alice-music-drums-3.opus">',
    '<speaker audio="alice-music-horn-1.opus">',
    '<speaker audio="alice-music-horn-2.opus">',
    '<speaker audio="alice-sounds-things-gun-1.opus">',
    '<speaker audio="alice-sounds-things-glass-1.opus">',
    '<speaker audio="alice-sounds-game-loss-1.opus">',
    '<speaker audio="alice-sounds-game-loss-2.opus">',
    '<speaker audio="alice-sounds-game-loss-3.opus">'
]

choiceValid = [
    'Выбери верное',
    'Какое правильно?',
    'Где верно?',
    "Выбирай!",
    "Вот"
]

# connection = sqlite3.connect('database.db')
# c = connection.cursor()

# Главный файл навыка

stress = Blueprint('sress', __name__)

basepath = 'data/data.json'
try:
    data = open('stress/data/data.json')
except:
    data = open('modules_alice/data/stress/data.json', 'r')
    basepath = 'modules_alice/data/stress/data.json'
base = json.loads(data.read())
data.close()

justvowel = set("аоиеёэуюяы")


@stress.route('/sress', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    response = handle(request.json, response)  # Основная обработка

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def handle(req, res):
    user_id = req['session']['user_id']

    session = getSession(user_id)
    user_text = req['request']['original_utterance']

    if req['request']['original_utterance'].lower() != 'ping':
        addView()

    if req['request']['original_utterance'].lower() == 'stat_31415926':
        res['response']['text'] = 'Просмотров: ' + str(getViews()) + '\n  Нет в БД, но спрашивали:\n'
        r = connection.execute('SELECT * FROM `not_found` ORDER BY count DESC')
        r = r.fetchall()
        for i in r:
            res['response']['text'] += ', '.join(list(map(str, i))) + '\n'
        return res

    if user_text.lower() == 'помощь' or user_text.lower() == 'что ты умеешь' or user_text.lower() == 'что ты умеешь?':
        res['response']['text'] = 'Я помогу тебе узнать правильное ударение в частоошибаемых русских словах.' \
                                  ' Просто напиши мне слово или выбери доступные действия.' \
                                  ' Со мной также можно сыграть в игру: ' \
                                  'я буду предлагать варианты слов, а тебе нужно будет выбрать правильный'
        res['response']['buttons'] = get_suggests(user_id)
        sessionStorage[user_id] = session
        return res
    elif (user_text.lower() == 'меню'):
        res = responseForMenu(res, user_id)
        session['action'] = 'new'
        sessionStorage[user_id] = session
        return res

    elif (user_text.lower() == 'ещё' or user_text.lower() == 'еще') and session['action'] == 'newgame':
        res['response']['text'] = randomElem(choiceValid)
        res['response']['buttons'] = get_suggests(user_id, 'newgame')
        sessionStorage[user_id] = session
        return res

    elif (user_text.lower() == 'ещё' or user_text.lower() == 'еще') and session['action'] == 'rand':
        session['action'] = 'rand'
        sessionStorage[user_id] = session
        return responseForRand(res, user_id)

    elif req['session']['new'] or user_id not in sessionStorage.keys():
        # New user
        sessionStorage[user_id] = newSession()
        if (user_text == ''):
            res['response']['text'] = 'Привет! Не хочешь немного орфоэпии? Выбери действие или напиши слово.'
            res['response']['tts'] = 'Привет! Не хочешь немного орфо+эпии? Выбери действие или напиши слово.'
            res['response']['buttons'] = get_suggests(user_id)
            return res

    elif (user_text.lower() == 'игра'):
        res['response']['text'] = randomElem(choiceValid)
        res['response']['buttons'] = get_suggests(user_id, 'newgame')
        return res

    elif session['action'].lower() == 'game':
        r = responseForGame(res, user_id, user_text, session)
        session = r[1]
        sessionStorage[user_id] = session
        return r[0]

    elif user_text.lower() == 'случайное слово':
        session['action'] = 'rand'
        sessionStorage[user_id] = session
        return responseForRand(res, user_id)

    if user_text.lower().count('скажи ударение в слове') != 0:
        user_text = user_text.lower().split()[-1]

    i = findByWord(base, user_text.lower())

    if (i == -1):
        web = getSressWeb(user_text.lower())
        # res['response']['text'] = str(web) + user_text.lower()
        # return res
        if (web != -1):
            res['response']['text'] = makeSress(user_text.lower(), web)
            res['response']['tts'] = ttsWordCapital(res['response']['text'])
            base.append({
                "word": user_text.lower(),
                "sress": web
            })
            json.dump(base, basepath)
        else:
            res['response']['text'] = 'Не знаю такого слова'
            res['response']['tts'] = 'Не знаю такого сл+ова'
            notFoundWord(user_text.lower())
    else:
        res['response']['text'] = makeSress(base[i]['word'], base[i]['sress'])
        res['response']['tts'] = ttsWordCapital(res['response']['text'])

    res['response']['buttons'] = get_suggests(user_id)

    sessionStorage[user_id] = session

    return res

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


def genApropr(prox):
    out = []
    for i in prox:
        out.append({"http": i, "https": i})
    return out

def getSressWeb(word):
    # specify the url
    quote_page = u'http://где-ударение.рф/в-слове-'
    quote_page += word.lower() + '/'
    url = quote_page
    parts = list(urlsplit(url))

    parts[0] = quote(parts[0], safe=':/?&')
    parts[1] = parts[1].encode('idna').decode('ascii')
    parts[2] = quote(parts[2], safe=':/?&')
    url = urlunsplit(parts)

    req = urlrequest.Request(url)
    try:
        data = urllib.request.urlopen(req).read()
    except Exception as e:
        return -1

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(data, 'html.parser')

    # Take out the <div> of name and get its value
    name_box = soup.find('div', attrs={'class': 'rule'})

    out = ''
    for i in name_box.contents:
        out += i.string
    out = out.strip()
    out = out.split('—')[-1].strip()

    punctuation = set(string.punctuation)

    out2 = ''

    uppercase = set('АОИЕЁЭУЮЯЫ')

    ud = 0
    for i in range(len(out)):
        if not out[i] in punctuation:
            out2 += out[i]
        if out[i] in uppercase:
            ud = i
    out = out2

    return ud


def get_suggests(user_id, action='new'):
    global sessionStorage

    session = getSession(user_id)  # current session
    suggests = []

    if (action == 'new'):
        suggests.append({
            "title": "Случайное слово",
            "hide": False
        })
        suggests.append({
            "title": "Игра",
            "hide": False
        })
    elif action == 'newgame':
        for i in getNewGame(user_id):
            suggests.append(i)
            session['asked'].append(i['title'].lower())

    sessionStorage[user_id] = session  # Save changes to global sessionStorage

    return suggests


# Find index of paronims dictionary in base
# a - base with paronims
# search - search word
def findByWord(a, search):
    for i in range(len(a)):
        if (a[i]['word'].lower() == search):
            return i
    return -1


def getNewGame(session):
    allWords = []
    correctvowels = {}
    id = session

    for i in base:
        allWords.append(i['word'].lower())
        correctvowels[i['word'].lower()] = (i['sress'])

    allWords = set(allWords)
    session = getSession(id)

    alreadyWords = set(session['asked'])
    if abs(len(alreadyWords) - len(allWords)) < 10:
        session['asked'] = []
        alreadyWords = set()

    possible = list(allWords.difference(alreadyWords))

    words = []
    iter = 0

    while len(words) <= 1:
        if iter > 10:
            possible = list(allWords)
            session['asked'] = []
        words = []
        iter += 1
        w_index = random.randint(0, len(possible) - 1)
        t = possible[w_index].strip()

        if 'ё' in set(t):
            continue

        vowels = []

        start = 0
        stop = len(t)

        if (t.find('(') > 0):
            stop = t.find('(')
        if t.find('(') == 0:
            start = t.find(')') + 1

        for i in range(start, stop):
            if t[i].lower() in justvowel:
                vowels.append(i)

        rightWord = ''

        for i in vowels:
            if (correctvowels[t] == i):
                rightWord = makeSress(t, i)
            words.append({
                "title": makeSress(t, i),
                "hide": True
            })

        words.append({
            "title": "Меню",
            "hide": False
        })
        session['right'] = rightWord
        session['action'] = 'game'

        sessionStorage[id] = session
    return words


def randWord(u_id):
    session = getSession(u_id)
    allWords = []
    for i in base:
        t = i['word'].lower()
        i = i['sress']
        allWords.append(makeSress(t, i))
    allWords = set(allWords)
    alreadyWords = set(session['asked'])
    possible = list(allWords.difference(alreadyWords))

    out = possible[random.randint(0, len(possible) - 1)]
    session['asked'].append(out)

    sessionStorage[u_id] = session
    return out


def newSession():
    return {'action': 'new', 'sugg': [], 'right': "", "asked": []}


def getSession(id):
    if not id in set(sessionStorage.keys()):
        sessionStorage[id] = newSession()
    session = sessionStorage[id]

    return session


def responseForMenu(res, user_id):
    res['response']['text'] = 'Доступные действия'
    res['response']['buttons'] = get_suggests(user_id)
    return res


def responseForRand(res, user_id):
    res['response']['text'] = randWord(user_id)
    res['response']['tts'] = ttsWordCapital(res['response']['text'])
    res['response']['buttons'] = [
        {
            "title": "Ещё",
            "hide": True
        },
        {
            "title": "Меню",
            "hide": False
        }
    ]
    return res


def responseForGame(res, user_id, user_text, session):
    if (user_text == session['right']):
        res['response']['text'] = 'Верно!\nТак же ответили ' + str(alsoAsked(user_text)) + '%.'
        res['response']['tts'] = 'Верно!' + randomWin()
    else:
        if user_text.lower() != session['right'].lower():
            session['action'] = 'new'
            res = responseForMenu(res, user_id)
            return [res, session]

        res['response']['text'] = 'Неверно!\nПравильно так: ' + session['right'] + '.\nОшиблись как вы: ' + str(
            alsoAsked(user_text)) + '%.'
        res['response']['tts'] = 'Неверно! Правильно так: ' + ttsWordCapital(session['right']) + randomFail()

    statChoice(user_text)
    session['action'] = 'newgame'
    res['response']['buttons'] = [
        {
            "title": "Ещё",
            "hide": True
        }, {
            "title": "Меню",
            "hide": False
        }
    ]
    return [res, session]


def makeSress(word, i):
    return word[0:i] + word[i].upper() + word[i + 1:]


def notFoundWord(word):
    return 0
    res = connection.execute('SELECT * FROM `not_found` WHERE `word`="' + word.lower() + '"')
    fetch = res.fetchall()
    if (len(fetch) == 0):
        connection.execute('INSERT INTO `not_found` VALUES ("' + word.lower() + '", "1")')
        connection.commit()
        return
    res = fetch[0]
    count = int(res[-1]) + 1
    connection.execute("UPDATE `not_found` SET 'count'=" + str(count) + ' WHERE `word`="' + word.lower() + '"')
    connection.commit()


def statChoice(choice):
    return 0
    res = connection.execute('SELECT * FROM `words_choice` WHERE `choice`="' + choice + '"')
    fetch = res.fetchall()
    if (len(fetch) == 0):
        connection.execute('INSERT INTO `words_choice` VALUES ("' + choice.lower() + '", "' + choice + '", 1)')
        connection.commit()
        return
    res = fetch[0]
    count = int(res[-1]) + 1
    connection.execute("UPDATE `words_choice` SET 'count'=" + str(count) + ' WHERE `choice`="' + choice + '"')
    connection.commit()


def addView(name='sress'):
    return 0
    res = connection.execute('SELECT * FROM `visits_count` WHERE `name`="' + name + '"')
    fetch = res.fetchall()
    if (len(fetch) == 0):
        connection.execute('INSERT INTO `visits_count` VALUES ("' + name + '", 1)')
        connection.commit()
        return
    res = fetch[0]
    count = int(res[-1]) + 1
    connection.execute("UPDATE `visits_count` SET 'count'=" + str(count) + ' WHERE `name`="' + name + '"')
    connection.commit()


def getViews(name='sress'):
    return 0
    res = connection.execute('SELECT * FROM `visits_count` WHERE `name`="' + name + '"')
    fetch = res.fetchall()
    if (len(fetch) == 0):
        return 0
    res = fetch[0]
    count = int(res[-1])
    return count


def ttsWord(word, i):
    return word[0:i] + "+" + word[i:]


def ttsWordCapital(word):
    out = ''
    capitals = set("АОИЕЁЭУЮЯ")
    for i in word:
        if i in capitals:
            out += "+"
        out += i
    return out


def randomFail():
    return failSounds[random.randint(0, len(failSounds) - 1)]


def randomWin():
    return winSounds[random.randint(0, len(winSounds) - 1)]


def randomElem(arr):
    return arr[random.randint(0, len(arr) - 1)]


def alsoAsked(name):
    return 0
    res = connection.execute('SELECT `count` FROM `words_choice` WHERE `choice`="' + name + '"')
    res = res.fetchall()
    s = 0
    s_all = 0
    for i in res:
        s += int(i[0])

    res_all = connection.execute('SELECT `count` FROM `words_choice` WHERE `group`="' + name.lower() + '"')
    res_all = res_all.fetchall()
    for i in res_all:
        s_all += int(i[0])

    if s == 0:
        proc = 0
    else:
        proc = (s_all * 100) / s

    # proc = 'SELECT count FROM `words_choice` WHERE `group`="' + name.lower() + '"'

    proc = round(float(proc), ndigits=1)

    return proc
