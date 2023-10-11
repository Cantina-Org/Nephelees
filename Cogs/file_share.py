from flask import send_from_directory, url_for, render_template
from Utils.utils import salt_password, user_login


def file_share_cogs(ctx, database, share_path, short_name=None):
    row = database.select('''SELECT * FROM cantina_nephelees.file_sharing WHERE file_short_name=%s''', (short_name,), 1)
    is_login = user_login(database, ctx)
    if not row[4]:
        if not row[5]:
            return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
        elif row[5] != "" and ctx.args.get('password') != "":
            data = database.select('''SELECT salt FROM cantina_administration.user WHERE user_name=%s''', (row[2],), 1)
            if salt_password(ctx.args.get('password'), data, database, ctx) == row[5]:
                return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
            else:
                return render_template('redirect/r-share-file-with-password.html', short_name=short_name)
        elif row[5] != "" and ctx.args.get('password') == "":
            return render_template('redirect/r-share-file-with-password.html', short_name=short_name)

    elif row[4]:
        if is_login[0]:
            return send_from_directory(directory=share_path + '/' + row[2], path=row[1])
        elif is_login == 'UserNotFound':
            return url_for('login')
