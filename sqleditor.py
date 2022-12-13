import sqlite3
import json
import time


def __init__(path):
    global dbpath
    dbpath = path


def open():  # открылил соединение с бд
    global cursor, connected_database
    connected_database = sqlite3.connect(dbpath + "database.db", check_same_thread=False, timeout=7)
    sqlite3.threadsafety = 2
    cursor = connected_database.cursor()


def close():  # открылил соединение с бд
    global cursor, connected_database
    connected_database.close()


def usermode(ID):  # Проверка юзермода
    open()
    found_item = cursor.execute("SELECT MODE FROM users WHERE ID=?", [(str(ID))]).fetchall()
    close()
    if len(found_item) == 0:
        # adduser(ID, username, name, chattype)
        return False
    else:
        return str(found_item[0][0])


def idbyuname(uname):
    open()
    found_item = cursor.execute("SELECT ID FROM users WHERE username LIKE ?", [(str(uname))]).fetchall()
    close()
    if len(found_item) == 0:
        return False
    else:
        return str(found_item[0][0])


def unamebyid(ID):
    open()
    found_item = cursor.execute("SELECT username FROM users WHERE ID=?", [(str(ID))]).fetchall()
    close()
    if len(found_item) == 0:
        return False
    else:
        return str(found_item[0][0])


def namebyid(ID):
    open()
    found_item = cursor.execute("SELECT name FROM users WHERE ID=?", [(str(ID))]).fetchall()
    close()
    if len(found_item) == 0:
        return False
    else:
        return str(found_item[0][0])


def adduser(ID, username='', name='', chattype=''):  # добавить нового полльзователя
    open()
    found_item = cursor.execute("SELECT MODE FROM users WHERE ID=?", [(str(ID))]).fetchall()
    if len(found_item) != 0:
        connected_database.close()
        return None
    cursor.execute(
        "INSERT INTO users (ID, MODE, username, name, chattype) VALUES ('{}', 'start', '{}', '{}', '{}')".format(
            ID,
            username,
            name,
            chattype
        )
    )
    connected_database.commit()
    close()


def addtask(ID, task):  # добавить нового полльзователя
    open()
    query = "INSERT INTO tasks ("\
            "status, "\
            "createdby, "\
            "text, "\
            "WID, "\
            "CID, "\
            "year, "\
            "month, "\
            "day, "\
            "hour, "\
            "minute"\
            ") VALUES ("\
            "'new', "\
            "'{}', "\
            "'{text}', "\
            "'{user}', "\
            "'{controller}', "\
            "'{year}', "\
            "'{month}', "\
            "'{day}', "\
            "'{hour}', "\
            "'{minute}');".format(ID, **task)

    cursor.execute(query)
    lid = cursor.lastrowid
    connected_database.commit()
    close()
    return lid


def gettask(ID):
    open()
    found_item = cursor.execute("SELECT t.*, u.username as user, u.name "
                                "FROM tasks as t LEFT JOIN users as u "
                                "ON t.WID = u.ID WHERE t.ID=?", [(str(ID))]).fetchone()
    close()
    if len(found_item) == 0:
        return False
    else:
        rowDict = dict(zip([c[0] for c in cursor.description], found_item))
        return rowDict


def edittaskstatus(ID, status):
    open()
    cursor.execute("UPDATE tasks SET status = '{}' WHERE ID = '{}'".format(status, ID))
    connected_database.commit()
    close()


def edittaskdate(ID, day, month, year):
    open()
    cursor.execute("UPDATE tasks SET day='{}', month='{}' , year='{}' WHERE ID = '{}'".format(day, month, year, ID))
    connected_database.commit()
    close()


def gettasks(ID, rule=0):
    open()
    ra = []
    if rule == 0:
        query = "SELECT t.*, u.username as user, u.name " \
                "FROM tasks as t LEFT JOIN users as u " \
                "ON t.WID = u.ID " \
                "WHERE t.WID=? and t.status!='complete' and t.status!='canceled';"
    elif rule == 1:
        query = "SELECT t.*, u.username as user, u.name " \
                "FROM tasks as t LEFT JOIN users as u " \
                "ON t.CID = u.ID " \
                "WHERE t.CID=? and t.status!='complete' and t.status!='canceled';"
    else:
        query = "SELECT t.*, u.username as user, u.name " \
                "FROM tasks as t LEFT JOIN users as u " \
                "ON t.WID = u.ID " \
                "WHERE t.WID=? and t.status!='complete' and t.status!='canceled';"
    found_item = cursor.execute(query, [(str(ID))]).fetchall()
    close()
    if len(found_item) == 0:
        return False
    else:
        for k in found_item:
            ra.append(dict(zip([c[0] for c in cursor.description], k)))
        return ra


def tasks( time, data, WID, text, ):  # добавить новое задание
    open()
    cursor.execute("INSERT INTO tasks('time','data','WID', 'text')"
                   " VALUES ('{time}', '{WID}', "
                   " '{data}','{text}')")

    connected_database.commit()
    close()

def editusermode(ID, mode):  # изменить юзермод
    open()
    cursor.execute("UPDATE users SET MODE = '{}' WHERE ID = '{}'".format(mode, ID))
    connected_database.commit()
    connected_database.close()


def getbalance(ID):  # Вытащить баланс юзера
    open()
    found_item = cursor.execute("SELECT BALANCE FROM users WHERE ID=?", [(str(ID))]).fetchall()[0][0]
    connected_database.close()
    return round(float(found_item), 2)


def setTask(WID,CID, data,time,complete,):  # добавить транзу anymoney
    open()
    cursor.execute(
        "INSERT INTO tasks (WID, CID, data, time, complete) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(WID,
                                                                                                                CID,
                                                                                                                data,
                                                                                                                time,
                                                                                                                complete,
                                                                                                                False))
    connected_database.commit()
    connected_database.close()

def setSetting(WID,CID, data,time,complete,):
    open()
    cursor.execute(
        "INSERT INTO tasks (WID,"
        " CID, data, time, "
        "complete) VALUES ('{}', '{}', '{}', '{}', '{}',)".format(WID, CID, data, time, complete, False))

    connected_database.commit()
    connected_database.close()

def selectTasks():  # добавить транзу yoomoney
    open()
    found_item = cursor.execute("SELECT * FROM tasks WHERE complete=?", [(False)]).fetchall()
    if len(found_item) != 0:
        connected_database.close()
        return []
    else:
        connected_database.close()
        return found_item


def get_payments():  # Список на проверку anymoney
    open()
    found_item = cursor.execute("SELECT ID, time, UID, amount FROM payments WHERE status=\"NEW\"").fetchall()
    connected_database.close()
    return found_item


def get_yoopayments():  # Список на проверку yoomoney
    open()
    found_item = cursor.execute("SELECT ID, time, UID, amount FROM yoopayments WHERE status=\"NEW\"").fetchall()
    connected_database.close()
    return found_item


def get_payment(ID):  # Конкретная транза anymoney
    open()
    found_item = cursor.execute("SELECT * FROM payments WHERE ID='{}'".format(ID)).fetchall()[0]
    connected_database.close()
    return found_item


def get_yoopayment(ID):  # Конкретная транза yoomoney
    open()
    found_item = cursor.execute("SELECT * FROM yoopayments WHERE ID='{}'".format(ID)).fetchall()[0]
    connected_database.close()
    return found_item


def update_payment(ID, mode):  # изменение статуса транзы am
    open()
    cursor.execute("UPDATE payments SET status = '{}' WHERE ID = '{}'".format(mode, ID))
    connected_database.commit()
    connected_database.close()


def update_yoopayment(ID, mode):  # изменение статуса транзы ym
    open()
    cursor.execute("UPDATE yoopayments SET status = '{}' WHERE ID = '{}'".format(mode, ID))
    connected_database.commit()
    connected_database.close()


def update_userbalance(ID, balance, action='+'):  # Пополнение баланса юзера (иногда списание)
    open()
    cursor.execute("UPDATE users SET BALANCE = BALANCE {} '{}' WHERE ID = '{}'".format(action, float(balance), ID))
    connected_database.commit()
    connected_database.close()


def update_userrefbalance(ID, balance, action='-'):
    open()
    cursor.execute("UPDATE users SET REFMONEY = REFMONEY {} '{}' WHERE ID = '{}'".format(action, float(balance), ID))
    connected_database.commit()
    connected_database.close()


def update_userbalance_manual(username, balance, action='+'):  # Пополнение баланса юзера (иногда списание)
    open()
    found_item = cursor.execute("SELECT MODE FROM users WHERE ID=?", [(str(username))]).fetchall()
    if len(found_item) == 0:
        return False
    cursor.execute("UPDATE users SET BALANCE = BALANCE {} '{}' WHERE ID = '{}'".format(action, float(balance), username))
    connected_database.commit()
    connected_database.close()
    return True

def update_userreferalbalance(ID, balance, action='+'):  # Пополнение баланса юзера (иногда списание)
    open()
    cursor.execute("UPDATE users SET REFMONEY = REFMONEY {} '{}' WHERE ID = '{}'".format(action, float(balance), ID))
    connected_database.commit()
    connected_database.close()


def set_setting(key, value):  # Добавить настройку
    open()
    cursor.execute("INSERT INTO settings VALUES ('{}', '{}')".format(key, json.dumps(value)))
    connected_database.commit()
    connected_database.close()


def update_setting(key, value):  # Обновить настройку
    open()
    cursor.execute("UPDATE settings SET value = '{}' WHERE key = '{}'".format(json.dumps(value), key))
    connected_database.commit()
    connected_database.close()


def get_setting(key):  # Получить настройку
    open()
    found_item = cursor.execute("SELECT value FROM settings WHERE key='{}'".format(key)).fetchall()
    if found_item == []:
        return ''
    found_item = found_item[0][0]
    connected_database.close()
    return json.loads(found_item)


def get_settings():  # Получить все настройки (для дампа бд)
    open()
    found_item = cursor.execute("SELECT * FROM settings").fetchall()
    found_item = found_item
    connected_database.close()
    return found_item


def get_paymentsstat():  # Получить статистику оплат
    open()
    yooamount = cursor.execute("SELECT SUM(amount) FROM yoopayments WHERE status = 'success'"
                               " and time > {}".format(time.time()-60*60*24)).fetchall()[0][0]
    if yooamount:
        yooamount = float(yooamount)
    else:
        yooamount = 0
    anyamount = cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'success'"
                               " and time > {}".format(time.time()-60*60*24)).fetchall()[0][0]
    if anyamount:
        anyamount = float(anyamount)
    else:
        anyamount = 0
    connected_database.close()
    return {'yoo': yooamount, 'any': anyamount}

