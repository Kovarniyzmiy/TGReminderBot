import configparser
import json
import logging
import time
import traceback
from datetime import datetime
import re
from addons import *
from tgcalendar import tgcalendar

import sqleditor as sql
import telepot

from telepot.loop import MessageLoop


msgarr = {
    'start': 'Этот бот поможет вам контролировать выполнение задач в вашей команде.\n▫️'
             'Задачи на себя или'
             ' на других исполнителей можно ставить прямо в Телеграм.\n▫️'
             'Каждая задача имеет исполнителя'
             ' и дату исполнения.\n▫️За день до выполнения задачи исполнителю приходит напоминание, что'
             ' надо внести отчет. Если отчет не вносится, то бот напоминает о задаче каждый'
             ' день.\n▫️Исполнитель может внести отчет “Выполнено” либо попросить снять контроль'
             ' или перенести на другую дату.\n▫️Контролирующий может принять отчет, отклонить или'
             ' перенести на другой срок.\n\nВы можете выставлять задачи двумя способами:\n1. В общем'
             ' чате с командой (для этого нужно добавить бот в чат и сделать его администратором).\n2.'
             ' В этом боте.\n\nКак поставить задачу:\nПоставьте в начале сообщения точку, после '
             'нее — текст задачи, исполнителя и дату выполнения. Для ввода имени исполнителя, напишите'
             ' @ и выберите из списка.\nНапример:\n. Внести правки в слайды {botuname} 30-06\n\nЕсли'
             ' вы не напишите исполнителя, то задача будет поставлена на вас.\nНапример:\n. Внести'
             ' правки в слайды 30-06\n\nПо умолчанию контролирующим является тот, кто поставил задачу.'
             ' Но вы можете указать кого-то другого контролирующим. Для этого нужно указать его имя'
             ' после исполнителя.\nНапример:\n. Внести правки в слайды'
             ' {botuname} @egor.boss 30-06\n\nЕсли хотите задать время, то после даты введите'
             ' время в формате ЧЧ:ММ.\nНапример:\n. Подготовить черновик презентации'
             ' {botuname} 30-06 12:15\n\nВремя указывать необязательно.\nЕсли вы укажете время,'
             ' то напоминание о задаче придет за сутки и за час до наступления этого времени, а'
             ' затем, если отчет не внесен, раз в сутки в это время.\n\nПросмотр списка задач\nВы'
             ' всегда можете просмотреть список задач, в которых вы исполнитель либо контролирующий.'
             ' Для этого в этом боте нажмите на кнопку Задачи.',
    'adminurl': '',
    'chatstart':
        'Приветствую! \n'
        'Сделайте @{botuname} администратором, чтобы вы могли выставлять задачи прямо в этой группе '
        '(Редактирование группы > Администраторы)\n\n'
        'Для вывода доступных функций напишите \help',
    'userfounderror':
        '😅 Извините, задача от {name} НЕ создана\n'
        '{text}\n'
        'Причина:\n'
        '{uname} - не зарегистрирован в боте\n\n'
        'Для регистрации {uname} нужно зайти в @{botuname} и нажать там Старт. нажать на кнопку 👇',
    'notasks': 'Сейчас у вас нет заданий!'
}


def msghandler(data):
    if 'new_chat_participant' in data:
        pass
    elif 'left_chat_participant' in data:
        pass
    elif 'photo' in data:
        pass
    else:
        handler(data)


def skip(data):
    ''


def new_chat_participant(data):
    cid = data['chat']['id']
    if 'new_chat_participant' in data:
        if 'username' in data['new_chat_participant']:
            if data['new_chat_participant']['username'] == bot_uname:
                bot.sendMessage(cid, msgarr['chatstart'].format(botuname=bot_uname))


def left_chat_participant(data):
    # print('left_chat_participant', data)
    ''


def parseTask(text, uid=""):
    now = datetime.now()
    retarray = {
        "year": '',
        "month": '',
        "day": '',
        "hour": '',
        "minute": '',
        'user': '',
        'controller': '',
        'text': '',
        'complete': False,
    }

    taskarray = text.split(" ")
    taskarray.pop(0)
    finaltext = ''
    usercount = 0
    nowtime = {
        "hour": int(now.hour),
        "minute": int(now.minute),
    }
    today = {
        "year": now.year,
        "month": now.month,
        "day": now.day,
    }

    for i in taskarray:
        if i == '':
            continue
        elif re.match(r'^([0-9]|0[0-9]|1?[0-9]|2[0-3]):[0-5]?[0-9]$', i):
            ts = i.split(':')
            retarray['hour'] = ts[0]
            retarray['minute'] = ts[1]
        elif re.match(r'^([0-9]|0[0-9]|1?[0-2])-[0-3]?[0-9]$', i):
            ds = i.split('-')
            retarray['month'] = ds[0]
            retarray['day'] = ds[1]
        elif '@' in i:
            if usercount == 0:
                usid = sql.idbyuname(i.replace('@', ''))
                if usid:
                    retarray['user'] = usid
                    usercount += 1
                else:
                    retarray['user'] = i
                    retarray['usererror'] = True
            else:
                cuid = sql.idbyuname(i.replace('@', ''))
                if cuid:
                    retarray['controller'] = cuid
                else:
                    retarray['controller'] = i
                    retarray['controllererror'] = True
        else:
            finaltext += i + ' '
    if not retarray['user']:
        retarray['user'] = uid
    if not retarray['controller']:
        retarray['controller'] = uid
    retarray['text'] = finaltext

    if retarray['hour']:
        if int(retarray['hour']) == nowtime['hour']:
            if int(retarray['minute']) <= nowtime['minute']:
                retarray['hour'] = ''
                retarray['minute'] = ''
        elif int(retarray['hour']) <= nowtime['hour']:
            retarray['hour'] = ''
            retarray['minute'] = ''

    for k, v in today.items():
        if not retarray[k]:
            retarray[k] = v
    return retarray


def genTaskText(task):
    text = '🆕 Задача от {user}\n' \
           '*{text}*\n'
    if task['day'] and task['month']:
        if task['hour'] and task['minute']:
            text += 'Срок: {hour}:{minute} {day}-{month}'
        else:
            text += 'Срок: {day}-{month}'
        if int(datetime.now().year) < int(task['year']):
            text += '-{year}'
        text += '\n'
    text = text.format(**task)
    return text


def genRetTaskText(task):
    text = '🆕 Задача от {user}\n' \
           '*{text}*\n'
    if task['day'] and task['month']:
        if task['hour'] and task['minute']:
            text += 'Срок: {hour}:{minute} {day}-{month}'
        else:
            text += 'Срок: {day}-{month}'
        if int(datetime.now().year) < int(task['year']):
            text += '-{year}'
        text += '\n'
    if task['name'] != '':
        task['user'] = task['name']
    elif task['user'][0] != '@':
        task['user'] = '@' + task['user']

    text = text.format(**task)
    return text


def genCancelTaskText(task):
    text = '🚫 {user} отменяет задачу\n' \
           '*{text}*\n'
    if task['day'] and task['month']:
        if task['hour'] and task['minute']:
            text += 'Срок: {hour}:{minute} {day}-{month}'
        else:
            text += 'Срок: {day}-{month}'
        if int(datetime.now().year) < int(task['year']):
            text += '-{year}'
        text += '\n'
    if task['name'] != '':
        task['user'] = task['name']
    elif task['user'][0] != '@':
        task['user'] = '@' + task['user']

    text = text.format(**task)
    return text


def genEditTaskText(task):
    text = '🔜 {user} перенесит задачу\n' \
           '*{text}*\n'
    if task['day'] and task['month']:
        if task['hour'] and task['minute']:
            text += 'Срок: {hour}:{minute} {day}-{month}'
        else:
            text += 'Срок: {day}-{month}'
        if int(datetime.now().year) < int(task['year']):
            text += '-{year}'
        text += '\n'
    if task['name'] != '':
        task['user'] = task['name']
    elif task['user'][0] != '@':
        task['user'] = '@' + task['user']

    text = text.format(**task)
    return text


def genCompleteTaskText(task):
    text = '✅ {user} поставил статус выполнено\n' \
           '*{text}*\n'
    # if task['day'] and task['month']:
    #     if task['hour'] and task['minute']:
    #         text += 'Срок: {hour}:{minute} {day}-{month}'
    #     else:
    #         text += 'Срок: {day}-{month}'
    #     if int(datetime.now().year) < int(task['year']):
    #         text += '-{year}'
    #     text += '\n'
    if task['name'] != '':
        task['user'] = task['name']
    elif task['user'][0] != '@':
        task['user'] = '@' + task['user']

    text = text.format(**task)
    return text


def genPrivTaskText(task):
    text = genTaskText(task)
    return text


def kicked(data):  # Если человек вышел из чата
    print('kicked', data)
    return None


def member(data):  # Если снова добавился после выхода
    uid = data['chat']['id']
    # sql.adduser(uid, '')
    # sql.editusermode(uid, 'polssogl')
    # bot.sendMessage('привет', reply_markup=InlineKeyboard(['Принимаю']))


def handler(data):  # Обработка всех сообщений
    try:
        cid = data['chat']['id']
        uid = data['from']['id']
        msgid = (cid, data['message_id'])  # айди сообщения
        chattype = data['chat']['type']
        text = data['text']
        usermode = sql.usermode(uid)

        if 'username' in data['chat']:
            username = data['chat']['username']
        elif data['from'] and 'username' in data['from']:
            username = data['from']['username']
        else:
            username = ''
        if 'first_name' in data['chat']:
            name = data['chat']['first_name']
        else:
            name = ''
        if not usermode:
            sql.adduser(uid, username, name, chattype)
            usermode = 'start'

        # if usermode == 'start':  # Первый шаг нового юзера
        #     sql.editusermode(uid, 'menu')
        # elif text == 'Привет':
        #     bot.sendMessage(uid, 'Приветствую. Сделайте {} администратором,'
        #                          ' чтобы вы могли выставлять задачи прямо в этой группе'
        #                          ' (Редактирование группы > Администраторы)'.format(bot_uname))

        if '/start' in text:
            sql.editusermode(uid, 'main')
            bot.sendMessage(uid, msgarr['start'].format(botuname="@" + bot_uname))
        elif '/control' == text:
            t = sql.gettasks(uid, rule=1)
            if t:
                for i in t:
                    lid = i['ID']
                    bot.sendMessage(uid,
                                    genRetTaskText(i),
                                    reply_markup=InlineKeyboard([[
                                        {'text': 'Отменить', 'callback': 'cancel_' + str(lid)},
                                        {'text': 'Перенести', 'callback': 'change_' + str(lid)},
                                        {'text': 'Выполнено', 'callback': 'complete_' + str(lid)},
                                    ]]),
                                    parse_mode='Markdown'
                                    )
                bot.deleteMessage(msgid)
            else:
                bot.sendMessage(uid, msgarr['notasks'])
                bot.deleteMessage(msgid)
        elif '/my' == text:
            t = sql.gettasks(uid, rule=0)
            if t:
                for i in t:
                    lid = i['ID']
                    bot.sendMessage(uid,
                                    genRetTaskText(i),
                                    reply_markup=InlineKeyboard([[
                                        {'text': 'Отменить', 'callback': 'cancel_' + str(lid)},
                                        {'text': 'Перенести', 'callback': 'change_' + str(lid)},
                                        {'text': 'Выполнено', 'callback': 'complete_' + str(lid)},
                                    ]]),
                                    parse_mode='Markdown'
                                    )
                bot.deleteMessage(msgid)
            else:
                bot.sendMessage(uid, msgarr['notasks'])
                bot.deleteMessage(msgid)
        elif text == 'Техподдержка':
            bot.sendMessage(
                uid,
                'Техподдержка', reply_markup=InlineKeyboard([
                    {
                        'text': 'Написать',
                        'url': msgarr['adminurl'],
                    }
                ])
            )
        elif text.lower() == '/help':
            bot.sendMessage(uid, 'для получения информации нажмите /start')
        elif text[0] == '.':
            task = parseTask(text, uid)

            if 'usererror' in task and task['usererror']:
                bot.sendMessage(cid,
                msgarr['userfounderror'].format(
                    botuname=bot_uname,
                    uname=task['user'],
                    name=username,
                    text=task['text']
                ), reply_markup=InlineKeyboard([
                    {'text': 'В бот!', 'url': 't.me/' + bot_uname + '?start=start'}
                ]))
                bot.deleteMessage(msgid)
            elif 'controllererror' in task and task['controllererror']:
                bot.sendMessage(cid,
                msgarr['userfounderror'].format(
                    botuname=bot_uname,
                    uname=task['controller'],
                    name=username,
                    text=task['text']
                ), reply_markup=InlineKeyboard([
                    {'text': 'В бот!', 'url': 't.me/' + bot_uname + '?start=start'}
                ]))
                bot.deleteMessage(msgid)
            else:
                wid = task['user']
                lid = sql.addtask(cid, task)
                name = sql.namebyid(task['user'])
                if name:
                    task['user'] = '@' + sql.unamebyid(task['user'])
                else:
                    task['user'] = '@' + sql.unamebyid(task['user'])
                task['controller'] = sql.unamebyid(task['controller'])
                if chattype != 'private':
                    bot.sendMessage(cid, genTaskText(task), parse_mode='Markdown')
                bot.sendMessage(wid,
                                genPrivTaskText(task),
                                reply_markup=InlineKeyboard([[
                                    {'text': 'Отменить', 'callback': 'cancel_' + str(lid)},
                                    {'text': 'Перенести', 'callback': 'change_' + str(lid)},
                                    {'text': 'Выполнено', 'callback': 'complete_' + str(lid)},
                                ]]),
                                parse_mode='Markdown')
                bot.deleteMessage(msgid)

    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())


def on_callback_query(data):  # Обработчик callback query
    try:
        print(data)
        uid = data['from']['id']  # айди юзера
        usermode = sql.usermode(uid)
        text = data['data']  # Текст каллбека
        msgid = (uid, data['message']['message_id'])  # айди сообщения

        if 'sel_' in text:
            if 'sel_d_' in text:
                pd = text.replace("sel_d_", "")
                tid, pd = pd.split('_')
                if pd != "-":
                    tpd = pd.split('-')
                    sql.edittaskdate(tid, tpd[0], tpd[1], tpd[2])
                    td = sql.gettask(tid)
                    bot.sendMessage(uid, genEditTaskText(td), parse_mode='Markdown')
                bot.deleteMessage(msgid)
            elif 'sel_m_' in text:
                pd = text.replace("sel_m_", "")
                tid, pd = pd.split('_')
                if pd != "-":
                    tc = tgcalendar(parse=pd, TID=tid)
                    bot.editMessageReplyMarkup(msgid, reply_markup=InlineKeyboard(tc.create()))
            elif 'sel_y_' in text:
                pd = text.replace("sel_y_", "")
                tid, pd = pd.split('_')
                if pd != "-":
                    tc = tgcalendar(parse=pd, TID=tid)
                    bot.editMessageReplyMarkup(msgid, reply_markup=InlineKeyboard(tc.create()))
        elif 'cancel_' in text:
            tid = text.replace("cancel_", '')
            ta = sql.gettask(tid)
            sql.edittaskstatus(tid, 'canceled')
            bot.editMessageText(msgid, genCancelTaskText(ta), parse_mode='Markdown')
        elif 'complete_' in text:
            tid = text.replace("complete_", '')
            ta = sql.gettask(tid)
            sql.edittaskstatus(tid, 'complete')
            bot.editMessageText(msgid, genCompleteTaskText(ta), parse_mode='Markdown')
        elif 'change_' in text:
            tid = text.replace("change_", '')
            td = sql.gettask(tid)
            tc = tgcalendar(month=td['month'], year=td['year'], TID=tid)
            bot.sendMessage(
                uid,
                'Выберите дату, на которую перенести задачу:', reply_markup=InlineKeyboard(tc.create())
            )
            bot.deleteMessage(msgid)
        # if text == 'Выполнено':
        #     task = parseTask(text)
        #     bot.sendMessage(uid, '✅ {user} выполнил задачу\n'
        #                          '{text}\n'
        #                          'Срок: {data} {time}\n\n'
        #                          'задача закрыта, вы можете сделать ее регулярной в течении 12 часов'.format(**task),
        #                 reply_markup=InlineKeyboard([['🔄 Сделать регулярным']]))

        if text == '🔄 Сделать регулярным':
            task = parseTask(text)

            bot.sendMessage(uid, 'На когда назначить следующее задание:\n'
                             'КАЛЕНДАРЬ ВЖУХ\n'
                             .format(**task))

    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    logging.basicConfig(filename=path + "main.log", level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')
    logging.info('------------------START LOGGING------------------')

    token = LOAD_CONFIG()
    sql.__init__(dbpath)
    bot = telepot.Bot(token)

    try:
        MessageLoop(bot, {'chat': msghandler,
                          'callback_query': on_callback_query,
                          'kicked': kicked,
                          'left_chat_participant': left_chat_participant,
                          'left_chat_member': skip,
                          'new_chat_participant': new_chat_participant,
                          'new_chat_member': skip,
                          'member': member}).run_as_thread()
    except Exception as e:
        logging.error(e)
    print(bot.getMe())
    bot_uname = bot.getMe()['username']


    # handler({'message_id': 60,
    #          'from': {'id': 5256680529, 'is_bot': False, 'first_name': 'Лев', 'username': 'LevAlexeevich',
    #                   'language_code': 'ru'},
    #          'chat': {'id': -780148312, 'title': '1', 'type': 'group', 'all_members_are_administrators': True},
    #          'date': 1670387422, 'text': '. здч'})


    while 1:
        time.sleep(1)
