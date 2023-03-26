from os import remove
from flask import render_template, url_for, redirect
from Utils.utils import user_login, make_log


def show_share_file_cogs(ctx, database, share_path, random_name=None):
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                    (ctx.cookies.get('userID'),), 1)
        try:
            row = database.select('''SELECT file_name, file_owner FROM cantina_cloud.file_sharing WHERE 
                file_short_name=%s''', (random_name,), 1)
            if random_name:
                remove(share_path + '/' + row[1] + '/' + row[0])
                database.insert('''DELETE FROM cantina_cloud.file_sharing WHERE file_short_name = %s;''', (random_name,)
                                )
        except Exception as error:
            make_log('Error', ctx.remote_addr, ctx.cookies.get('userID'), 2, str(error))
        all_share_file = database.select('''SELECT * FROM cantina_cloud.file_sharing''')
        return render_template('admin/show_share_file.html', user_name=user_name, all_share_file=all_share_file)

    else:
        make_log('login_error', ctx.remote_addr, ctx.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))
