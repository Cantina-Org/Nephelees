from hashlib import new
from os import mkdir
from uuid import uuid3, uuid1
from flask import render_template, url_for
from werkzeug.utils import secure_filename, redirect
from Utils.utils import user_login, salt_password, make_log


def add_user_cogs(ctx, database, dir_path, share_path):
    admin = 0
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        if ctx.method == 'GET':
            user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                        (ctx.cookies.get('userID'),))
            return render_template('admin/add_user.html', user_name=user_name)
        elif ctx.method == 'POST':

            if ctx.form['pword1'] == ctx.form['pword2']:
                data = ctx.form
                new_uuid = str(uuid3(uuid1(), str(uuid1())))
                new_salt = new('sha256').hexdigest()
                try:
                    for i in data:
                        if i == 'admin':
                            admin = 1
                        else:
                            pass

                    database.insert('''INSERT INTO cantina_administration.user(token, user_name, salt, password, 
                            admin, work_Dir) VALUES (%s, %s, %s, %s, %s, %s)''',
                                    (new_uuid, ctx.form['uname'], new_salt,
                                     salt_password(ctx.form['pword2'], new_salt, database, ctx,
                                                   new_account=True),
                                     admin,
                                     dir_path + '/' + secure_filename(ctx.form['uname'])))

                except Exception as error:
                    make_log('Error', ctx.remote_addr, ctx.cookies.get('userID'), 2, str(error))

                mkdir(dir_path + '/' + secure_filename(ctx.form['uname']))
                mkdir(share_path + '/' + secure_filename(ctx.form['uname']))
                make_log('add_user', ctx.remote_addr, ctx.cookies.get('userID'), 2,
                         'Created user token: ' + new_uuid)
                return redirect(url_for('admin_show_user'))
    else:
        make_log('Error', ctx.remote_addr, ctx.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))
