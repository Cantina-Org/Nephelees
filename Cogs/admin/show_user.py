from flask import render_template, url_for, redirect
from Utils.utils import user_login, make_log


def show_user_cogs(ctx, database, user_name=None):
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        if user_name:
            user_account = database.select('''SELECT * FROM cantina_administration.user WHERE user_name=%s''',
                                           (user_name,))

            return render_template('admin/specific_user_manager.html', user_account=user_account[0])
        else:
            all_account = database.select(body='''SELECT * FROM cantina_administration.user''')
            user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                        (ctx.cookies.get('userID'),))
            return render_template('admin/user_manager.html', user_name=user_name,
                                   all_account=all_account)
    else:
        make_log('Error', ctx.remote_addr, ctx.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))
