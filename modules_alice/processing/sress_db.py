all='''А
агЕнт
алфавИт
аэропОрты, им.п. мн.ч. 
Б
балОванный, прич. 
баловАть
баловАться 
Баловень (судьбы)
балУясь 
бАнты, им.п.мн.ч
бОроду, вин.п.ед.ч. 
бралА
бралАсь
бухгАлтеров, род.п. мн.н
В
вЕрба
вернА
вероисповЕдание
взялА
взялАсь
включЁн 
включЁнный
включИм
включИт
включИшь 
влилАсь
вложИв
вОвремя
ворвалАсь
воспринялА
воссоздалА
вручИт
Г
гналА
гналАсь
граждАнство
Д
давнИшний 
дефИс
диспансЕр
добелА
добралА
добралАсь
довезЁнный
дОверху
договорЁнность
дождалАсь
дозвонИтся
дозвонЯтся 
дозИровать
докраснА 
докумЕнт
донЕльзя
дОнизу
досУг
дОсуха
доЯр
Е
еретИк
Ж
жалюзИ, ср.р.и мн.ч. 
ждалА
жилОсь
З
завезенО
завезенЫ
завИдно
зАгнутый
зАгодя
закУпорив
закУпорить
зАнял
занялА
зАняло
занятА
зАнятый
заселЁн
запертА
зАсветло
зАтемно
звалА
звонИм 
звонИт
звонИшь
знАчимость
знАчимый
зимОвщик
И
избалОванный
издрЕвле
Иксы
импЕрский
инстИнкт
исключИт
Исстари
исчЕрпав
исчЕрпать
К
каталОг
квартАл
киломЕтр
клАла
клЕить
кОнусы,кОнусов
кормЯщий
корЫсть
крАла
крАлась
крАны
красИвее
красИвейший
кремЕнь, кремнЯ
кренИтся
кровоточАщий
кровоточИть
кУхонный
Л 
лгалА
лЕкторы
лЕкторов
лилА
лилАсь
ловкА
лыжнЯ
М
мЕстностей
мозаИчный
молЯщий
мусоропровОд
Н
навЕрх
навралА
наделИт
надОлго
надорвалАсь
нажИвший
нажитА
нажИлся
назвалАсь
накренИт
налилА
налИвший
налитА
намЕрение
нанЯвшийся
нарвалА
нарОст
насорИт
нАчал
началА
нАчали
начАв
начАвший
начАвшись
нАчатый
начАть 
нАчатые 
нЕдруг
недУг
некролОг
нЕнависть
ненадОлго
низведЁн
нОвости,новостЕй 
нОгтя, род.п ед.ч. 
нормировАть
О
обеспЕчение
обзвонИт
облегчИт
облегчИть
облилАсь
обнялАсь
обогналА
ободралА
ободрИть
ободрЁнный
ободрЁн
ободренА
ободрИшься
обострЁнный
обострИть
одолжИт 
озлОбить
оклЕить
окружИт
опломбировАть
опОшлят
определЁн
оптОвый
освЕдомиться, 
освЕдомишься
отбылА
отдалА
отдАв
Отзыв (на публикацию)
отключЁнный
откУпорил
отозвалА
отозвалАсь
Отрочество
П
партЕр 
перезвонИт
перелилА
плодоносИть повторЁнный
поделЁнный
поднЯв
позвалА
позвонИт, позвонИшь
полилА
положИл 
положИть
понЯв
понЯвший
пОнял, 
понялА 
портфЕль
пОручни
послАла
(вы) прАвы
пОчестей
(она) правА
прибЫв
прИбыл 
прибылА 
прИбыло
придАное
призЫв
прИнял
прИняли
принУдить
прИнятый
принялсЯ
принялАсь
приручЁнный
прожИвший
прозорлИва
процЕнт	Р
рвалА
С
свЁкла
сверлИт
сверлИшь
(она) серА
(вы)сЕры
сирОты
слИвовый
снялА
снятА
сОгнутый
создалА 
созданА
созЫв сорИт
срЕдства, им.п.мн.ч. 
срЕдствами 
стАтуя
столЯр
(она) стройнА
(oно) стрОйно
(вы)стрОйны

Т
тамОжня
тОрты
тОртов
тОтчас
У
убралА
убыстрИть
углубИть
укрепИт
Ц
цемЕнт
цЕнтнер
цепОчка
Ч
чЕлюстей
чЕрпать
Ш
шАрфы
шофЁр
Щ
щавЕль
щемИт
щЁлкать
Э
экспЕрт'''

import json

def whereSress(s):
    capitals = set('ЙЦУКЕНГШЩЗХЪЁФЫВАПРОЛДЖЭЯЧСМИТЬБЮ')
    for i in range(len(s)):
        if s[i] in capitals:
            return i
    return -1

def findByWord(a, search):
    for i in range(len(a)):
        if (a[i]['word'].lower() == search):
            return i
    return -1

base = '../data/stress/data/data.json'
existing = json.load(open(base))

all=all.replace(',','\n')
all = all.split('\n')

for i in all:
    i = i.strip()
    if (len(i) <= 1 or i.count('им.п')!=0 or i.count('ед.')!=0 or i.count('мн.н')!=0 or i.count('мн.ч')!=0):
        continue

    word = i.lower()
    sress = whereSress(i)

    if (sress == -1):
        continue

    if (findByWord(existing,word) == -1):
        existing.append({
            'word': word,
            'sress': sress
        })
        print(word)

json.dump(existing, open(base,'w'))