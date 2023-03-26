from flask import redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from Utils.utils import user_login, make_log, f_user_name


def download_file_cogs(ctx, database, dir_path):
    args = ctx.args

    user_token = ctx.cookies.get('userID')
    user_check = user_login(database, ctx)

    make_log('Download file', ctx.remote_addr, ctx.cookies.get('userID'), 1,
             dir_path + args.get('path') + args.get('item'))
    if user_check == 'UserNotFound':
        return redirect(url_for('login'))
    elif user_check[1]:
        return send_from_directory(dir_path + args.get('path'), path=secure_filename(args.get('item')))
    elif not user_check[1]:
        return send_from_directory(dir_path + '/' + f_user_name(user_token, database) + args.get('path'),
                                   path=secure_filename(args.get('item')))
