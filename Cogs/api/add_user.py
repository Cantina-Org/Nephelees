from hashlib import new
from uuid import uuid1, uuid3
from flask import escape, jsonify
from werkzeug.utils import secure_filename
from Utils.utils import make_log, salt_password


def add_user_api_cogs(ctx, database, dir_path):
    admin = False
    content = ctx.json
    row1 = database.select('''SELECT * FROM cantina_cloud.api where token=%s''', (escape(content['api-token']),), 1)
    row2 = database.select('''SELECT * FROM cantina_cloud.api_permission where token_api=%s''',
                           (escape(content['api-token']),), 1)
    if row2[8]:
        try:
            new_salt = new('sha256').hexdigest()
            new_uuid = str(uuid3(uuid1(), str(uuid1())))
            if content['admin'] == 1:
                admin = True

            database.insert('''INSERT INTO cantina_administration.user(token, user_name, salt, password, admin, 
                work_Dir)  VALUES (%s, %s, %s, %s, %s, %s)''', (new_uuid, escape(content['username']), new_salt,
                                                                salt_password(content['password'], new_salt, database,
                                                                              ctx),
                                                                admin,
                                                                dir_path + '/' + secure_filename(content['username'])))
            make_log(database, 'add_user_api', ctx.remote_addr, ctx.cookies.get('userID'), 4,
                     'Created User token: ' + new_uuid, escape(content['api-token']))
            return jsonify({
                "status-code": "200",
                "api-token": escape(content['api-token']),
                "user-to-create": escape(content['username']),
                "user-passsword-to-create": escape(content['password']),
                "user-permission-to-create": escape(content['admin']),
                "user-token-create": new_uuid
            })
        except KeyError as error:
            return 'L\'argument {} est manquant!'.format(str(error))
    else:
        if row1:
            make_log(database, 'add_api_error', ctx.remote_addr, content['api-token'], 4, 'Not enough permission',
                     content['api-token'])
            return jsonify({
                "status-code": "401",
                "details": "You don't have the permission to use that"
            })
        else:
            make_log(database, 'add_api_error', ctx.remote_addr, content['api-token'], 4, 'Not logged in',
                     content['username'])
            return jsonify({
                "status-code": "401",
                "details": "You must be login to use that"
            })
