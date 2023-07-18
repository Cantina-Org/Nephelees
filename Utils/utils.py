from hashlib import sha256
from os import path
from tarfile import open as tar_open
from argon2 import PasswordHasher

ph = PasswordHasher()


def make_log(database, action_name: str, user_ip: str, user_token: str, log_level: int, argument: str = None,
             content: str = None):
    if content:
        database.insert('''INSERT INTO cantina_administration.log(name, user_ip, user_token, argument, log_level) 
        VALUES (%s, %s, %s,%s,%s)''', (str(action_name), str(user_ip), str(content), str(argument), str(log_level)))
    else:
        database.insert('''INSERT INTO cantina_administration.log(name, user_ip, user_token, argument, log_level) 
        VALUES (%s, %s, %s,%s,%s)''', (str(action_name), str(user_ip), str(user_token), str(argument), str(log_level)))


def f_user_name(user_id, database):
    data = database.select("""SELECT user_name FROM cantina_administration.user WHERE token=%s""", (user_id,), 1)
    return data[0]


def salt_password(passwordtohash, user_name, database, ctx, new_password=False):
    try:
        if not new_password:
            try:
                data = database.select('''SELECT salt FROM cantina_administration.user WHERE user_name=%s''',
                                       (user_name,), 1)
                password = sha256(ph.verify(passwordtohash, data[0])).hexdigest().encode()
                return password
            except Exception as e:
                return 'User Not Found, ' + str(e)
        else:
            password = ph.hash(passwordtohash).encode()
            return password

    except AttributeError as error:
        make_log(database, 'Error', ctx.remote_addr, ctx.cookies.get('userID'), 2, str(error))
        return None


def user_login(database, ctx):
    data = database.select('''SELECT user_name, admin FROM cantina_administration.user WHERE token = %s''',
                           (ctx.cookies.get('token'),), 1)
    try:
        if data[0] != '' and data[1]:
            return True, True
        elif data[0] != '' and not data[1]:
            return True, False
        else:
            return False, False
    except Exception as error:
        return error


def make_tarfile(output_filename, source_dir):
    with tar_open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=path.basename(source_dir))
