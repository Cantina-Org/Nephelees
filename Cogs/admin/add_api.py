from uuid import uuid3, uuid1
from flask import url_for, redirect, render_template
from Utils.utils import make_log, user_login


def add_api_cogs(ctx, database):
    api_create_file, api_upload_file, api_delete_file, api_create_folder, api_delete_folder, api_share_file_folder, \
        api_delete_share_file_folder, api_delete_user, api_create_user = 0, 0, 0, 0, 0, 0, 0, 0, 0
    admin_and_login = user_login(database, ctx)
    if admin_and_login[0] and admin_and_login[1]:
        if ctx.method == 'GET':
            user_name = database.select('''SELECT user_name FROM cantina_administration.user WHERE token=%s''',
                                        (ctx.cookies.get('userID'),))

            return render_template('admin/add_api.html', user_name=user_name)
        elif ctx.method == 'POST':
            if ctx.form.get('api_create_file'):
                api_create_file = 1
            if ctx.form.get('api_upload_file'):
                api_upload_file = 1
            if ctx.form.get('api_delete_file'):
                api_delete_file = 1
            if ctx.form.get('api_create_folder'):
                api_create_folder = 1
            if ctx.form.get('api_delete_folder'):
                api_delete_folder = 1
            if ctx.form.get('api_share_file_folder'):
                api_share_file_folder = 1
            if ctx.form.get('api_delete_share_file_folder'):
                api_delete_share_file_folder = 1
            if ctx.form.get('api_create_user'):
                api_create_user = 1
            if ctx.form.get('api_delete_user'):
                api_delete_user = 1

            new_uuid = str(uuid3(uuid1(), str(uuid1())))
            database.insert('''INSERT INTO cantina_cloud.api(token, api_name, api_desc, owner) VALUES (%s, %s, %s, 
                %s)''', (new_uuid, ctx.form.get('api-name'), ctx.form.get('api-desc'), ctx.cookies.get(
                'userID')))
            database.insert('''INSERT INTO cantina_cloud.api_permission(token_api, create_file, upload_file, 
                delete_file, create_folder, delete_folder, share_file_and_folder, delete_share_file_and_folder, 
                create_user, delete_user) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                            (new_uuid, api_create_file,
                             api_upload_file,
                             api_delete_file,
                             api_create_folder,
                             api_delete_folder,
                             api_share_file_folder,
                             api_delete_share_file_folder,
                             api_create_user,
                             api_delete_user))

            make_log('add_api', ctx.remote_addr, ctx.cookies.get('userID'), 2,
                     'Created API token: ' + new_uuid)
            return redirect(url_for('admin_api_manager'))
    else:
        make_log('login_error', ctx.remote_addr, ctx.cookies.get('userID'), 2, database)
        return redirect(url_for('home'))
