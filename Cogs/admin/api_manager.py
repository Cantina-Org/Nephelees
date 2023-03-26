from flask import redirect, url_for, render_template
from Utils.utils import user_login, make_log


def api_manager_cogs(ctx, database, api_id=None):
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        if api_id:
            api = database.select('''SELECT * FROM cantina_cloud.api WHERE ID=%s''', (api_id,))
            return render_template('admin/specific_api_manager.html', api=api[0])
        else:
            api = database.select('''SELECT * FROM cantina_cloud.api''')
            return render_template('admin/api_manager.html', api=api)
    else:
        make_log('login_error', ctx.remote_addr, ctx.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))
