#!/usr/bin/python3.6
import json
import string

f = open('paronims.json')
data = json.loads(f.read())
f.close()

allow = set(string.ascii_letters + 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' + 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

for l in range(len(data['paronims'])):
    for j in range(1, 3):
        # print (str(j))
        word = data['paronims'][l]['word' + str(j)]
        ind = 0
        inds = len(word["meaning"])

        if ('— (.....' == word["meaning"] or word["meaning"] == '..' or 'только.' == word["meaning"] or '.' == word[
            "meaning"] or 'только с.' == word["meaning"]):
            word["meaning"] = ''
            data['paronims'][l]['word' + str(j)] = word
            continue

        for k in range(len(word["meaning"])):
            if (word["meaning"][k] in allow):
                ind = k
                break
        for k in range(len(word["meaning"]) - 1, -1, -1):
            if (word["meaning"][k] in allow):
                inds = k
                break
        # print(word["meaning"][ind], word["meaning"][inds-1])
        try:
            word["meaning"] = word["meaning"][ind].upper() + word["meaning"][ind + 1:inds + 1].strip() + '.'

            word["meaning"] = word["meaning"].replace('(', ',').replace(')', ',')
            word["meaning"] = word["meaning"].strip().replace('-', '').replace(',.', '')
        except:
            word["meaning"] = ''
        # print(word["meaning"])

        examples = []

        for k in range(len(word['examples'])):
            ind = 0
            inds = len(word['examples'][k])
            if (len(word['examples'][k]) <= 6):
                # print(word['examples'][k])
                continue

            if (',. 2.' == word['examples'][k] or word['examples'][k] == ',. 2.' or ')' == word['examples'][k] or '.' ==
                    word['examples'][k] or 'только с.' == word['examples'][k]):
                data['paronims'][l]['word' + str(j)] = word
                continue

            for i in range(len(word['examples'][k])):
                if (word['examples'][k][i] in allow):
                    ind = i
                    break
            for i in range(len(word['examples'][k]) - 1, -1, -1):
                if (word['examples'][k][i] in allow):
                    inds = i
                    break
            # print(word["meaning"][ind], word["meaning"][inds-1])
            try:
                word['examples'][k] = word['examples'][k][ind].upper() + word['examples'][k][
                                                                         ind + 1:inds + 1].strip() + '.'
                word['examples'][k] = word['examples'][k].replace('(', ',').replace(')', ',').strip()
                examples.append(word['examples'][k])
            except:
                pass
        word['examples'] = examples
        print(word)

        data['paronims'][l]['word' + str(j)] = word

f = open('paronims.json', 'w')
f.write(json.dumps(data))
f.close()
