from Utils.utils import make_log
from flask import escape, jsonify


def show_permission_cogs(ctx, database):
    content = ctx.json
    row1 = database.select('''SELECT * FROM cantina_administration.api where token=%s''', (escape(content['api-token']),
                                                                                           ), 1)
    row2 = database.select('''SELECT * FROM cantina_administration.api_permission where token_api=%s''',
                           (escape(content['api-token']),), 1)
    make_log(database, 'show_permission', ctx.remote_addr, escape(content['api-token']), 4, escape(content['api-token']))

    return jsonify({
        "status-code": "200",
        "api-token": escape(content['api-token']),
        "api-name": row1[2],
        "permission": {
            "create_file": row2[1],
            "upload_file": row2[2],
            "delete_file": row2[3],
            "create_folder": row2[4],
            "delete_folder": row2[5],
            "share_file_and_folder": row2[6],
            "delete_share_file_and_folder": row2[7],
            "create_user": row2[8],
            "delete_user": row2[9],
        }
    })