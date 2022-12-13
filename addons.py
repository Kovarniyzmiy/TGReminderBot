import configparser
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


token = ''
path = ''
dbpath = ''
# path = '/root/bot/'
# dbpath = '/root/bot/'


def LOAD_CONFIG():  # Подгрузка конфига
    global token
    config = configparser.ConfigParser()
    config.read(path + "settings.ini")
    token = config.get('Settings', 'BOT TOKEN')
    return token


def ReplyKeyboard(buttons):  # Упрощенная генерация ReplyKeyboardMarkup
    list1 = []
    list2 = []
    for key in buttons:
        if type(key) == list:
            for key2 in key:
                if type(key2) == str:
                    list2.append(KeyboardButton(text=key2))
            if list2 != []:
                list1.append(list2)
                list2 = []
        elif type(key) == str:
            list1.append([KeyboardButton(text=key)])

    return ReplyKeyboardMarkup(keyboard=list1, resize_keyboard=True)


def InlineKeyboard(buttons, page=1, indent=10,
                   multipage=False):  # Упрощенная генерация InlineKeyboardMarkup со страницой
    list1 = []
    list2 = []
    for key in buttons:
        if type(key) == list:
            for key2 in key:
                if type(key2) == str:
                    list2.append(InlineKeyboardButton(text=key2, callback_data=key2))
                elif type(key2) == dict:
                    if 'url' in key2.keys():
                        list2.append(InlineKeyboardButton(text=key2['text'], url=key2['url']))
                    elif 'callback' in key2.keys():
                        list2.append(InlineKeyboardButton(text=key2['text'], callback_data=key2['callback']))
                    elif 'game' in key2.keys():
                        list2.append(InlineKeyboardButton(text=key2['text'], callback_game=key2['game']))
            if list2 != []:
                list1.append(list2)
                list2 = []
        elif type(key) == str:
            list1.append([InlineKeyboardButton(text=key, callback_data=key)])
        elif type(key) == dict:
            if 'url' in key.keys():
                list1.append([InlineKeyboardButton(text=key['text'], url=key['url'])])
            elif 'callback' in key.keys():
                list1.append([InlineKeyboardButton(text=key['text'], callback_data=key['callback'])])

    if multipage:
        list1 = list1[(page - 1) * indent:page * indent]

        if page == 1:
            list1.append([InlineKeyboardButton(text='>>', callback_data="page" + str(page + 1))])
        elif page * indent >= len(buttons):
            list1.append([InlineKeyboardButton(text='<<', callback_data="page" + str(page - 1))])
        else:
            list1.append([InlineKeyboardButton(text='<<', callback_data="page" + str(page - 1)),
                          InlineKeyboardButton(text='>>', callback_data="page" + str(page + 1))])

    return InlineKeyboardMarkup(
        inline_keyboard=list1
    )
