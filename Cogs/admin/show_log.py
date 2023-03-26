from flask import render_template, redirect, url_for

from Utils.utils import user_login, make_log


def show_log_cogs(ctx, database, log_id=None):
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        if log_id:
            log = database.select('''SELECT * FROM cantina_administration.log WHERE ID=%s''', (log_id,), 1)
            return render_template('admin/specific_log.html', log=log)
        else:
            all_log = database.select('''SELECT * FROM cantina_administration.log''')
            return render_template('admin/show_log.html', all_log=all_log)
    else:
        make_log('login_error', ctx.remote_addr, ctx.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))
