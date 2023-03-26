from os import walk
from subprocess import check_output
from flask import render_template, redirect, url_for
from Utils.utils import user_login, make_log


def home_admin_cogs(ctx, database, dir_path):
    count = 0
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        for root_dir, cur_dir, files in walk(dir_path):
            count += len(files)
        main_folder_size = check_output(['du', '-sh', dir_path]).split()[0].decode('utf-8')
        user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                    (ctx.cookies.get('userID'),))
        return render_template('admin/home.html', data=user_name, file_number=count,
                               main_folder_size=main_folder_size)
    else:
        make_log('login_error', ctx.remote_addr, ctx.cookies.get('userID'), 2)
        return redirect(url_for('home'))
