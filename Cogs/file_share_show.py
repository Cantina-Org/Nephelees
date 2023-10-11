from flask import redirect, url_for, render_template


def file_share_show(ctx, database):
    if not ctx.cookies.get('token'):
        return redirect(url_for('login'))
    data = database.select('''SELECT user_name, admin FROM cantina_administration.user WHERE token = %s''',
                           (ctx.cookies.get('token'),), 1)
    if data[1]:
        file_shared = database.select('''SELECT * FROM cantina_nephelees.file_sharing''', None)
    else:
        file_shared = database.select('''SELECT * FROM cantina_nephelees.file_sharing WHERE 
        cantina_administration.file_sharing.file_owner = %s''', (str(data[0])))
    try:
        return render_template('show_share_file.html', cur=data, file_shared=file_shared)
    except IndexError:
        return redirect(url_for('login'))
