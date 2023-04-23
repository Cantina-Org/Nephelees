from flask import redirect, url_for, render_template


def home_cogs(ctx, database):
    if not ctx.cookies.get('token'):
        return redirect(url_for('login'))
    data = database.select('''SELECT user_name, admin FROM cantina_administration.user WHERE token = %s''',
                           (ctx.cookies.get('token'),), 1)
    try:
        return render_template('home.html', cur=data)
    except IndexError:
        return redirect(url_for('login'))
