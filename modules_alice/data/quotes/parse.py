#!/usr/bin/python3.6
import vk
import json

session = vk.Session('95b281c395b281c395b281c3ed95d425dd995b295b281c3ce799373392c3bcf1673cdbb')
api = vk.API(session, v='5.35', lang='ru', timeout=1000000)

f = open('cit.json', 'r')
out = list(set(json.loads(f.read())))
f.close()
print(len(out))


def parseG(url, n):
    group = api.wall.get(domain=url, count=n)

    out = []
    reclam = ['😇', 'заказ', 'менеджер', 'коиплектущие', 'магазин', 'vk.cc', 'vk', '👉 vk.cc', "DOMINIK", 'цена пугала',
              'акции', 'акция', 'iPhone 7', 'www', 'визитки', 'буклеты', 'брошюры', 'http']

    mat = list(set(json.loads(open('mat.json').read())))

    for i in group['items']:
        i = i['text']
        flag = False
        for j in reclam:
            if (i.find(j) != -1):
                flag = True
        for j in mat:
            if (i.find(j) != -1):
                flag = True

        if (not flag and i != ""):
            out.append(i)

    return out


pabl = ['skinnycatclub' ,'dimastoff132903768']

i = 0
for i in pabl:
    n = parseG(i, 10000)
    for j in n:
        out.append(j)

print(len(out))
f = open('cit.json', 'w')
f.write(json.dumps(out))
f.close()
