from datetime import datetime
from flask import make_response, redirect, url_for, render_template
from Utils.utils import salt_password, make_log


def login_cogs(ctx, database):
    if ctx.method == 'POST':
        user = ctx.form['nm']
        passwd = ctx.form['passwd']
        row = database.select(f'''SELECT user_name, password, token FROM cantina_administration.user WHERE password = %s 
        AND user_name = %s''', (salt_password(passwd, user, database, ctx), user), 1)

        try:
            make_log('login', ctx.remote_addr, row[2], 1, database)
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('userID', row[2])
            database.insert('''UPDATE cantina_administration.user SET last_online=%s WHERE token=%s''',
                            (datetime.now(), row[2]))
            return resp
        except Exception as error:
            make_log('Error', ctx.remote_addr, ctx.cookies.get('userID'), 2, str(error))
            return redirect(url_for("home"))

    elif ctx.method == 'GET':
        return render_template('login.html')
