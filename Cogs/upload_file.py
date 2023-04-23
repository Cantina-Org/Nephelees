from os import path
from flask import render_template, url_for, redirect
from werkzeug.utils import secure_filename
from Utils.utils import user_login, make_log, f_user_name


def upload_file_cogs(ctx, database, dir_path):
    args = ctx.args

    if ctx.method == 'GET':
        return render_template('upload_file.html')

    elif ctx.method == 'POST':
        user_token = ctx.cookies.get('token')
        user_check = user_login(database, ctx)

        if user_check == 'UserNotFound':
            return redirect(url_for('login'))
        elif user_check[1]:
            f = ctx.files['file']
            f.save(path.join(dir_path + args.get('path'), secure_filename(f.filename)))
            make_log('upload_file', ctx.remote_addr, ctx.cookies.get('token'), 1, database,
                     path.join(dir_path + args.get('path'), secure_filename(f.filename)))
            return redirect(url_for('file', path=args.get('path')))
        elif not user_check[1]:
            f = ctx.files['file']
            f.save(path.join(dir_path + '/' + f_user_name(user_token, database) + args.get('path'),
                             secure_filename(f.filename)))
            make_log('upload_file', ctx.remote_addr, ctx.cookies.get('token'), 1,
                     path.join(dir_path + args.get('path'), secure_filename(f.filename)))
            return redirect(url_for('file', path=args.get('path')))
