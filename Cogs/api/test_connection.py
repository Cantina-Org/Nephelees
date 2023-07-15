from Utils.utils import make_log
from flask import escape, jsonify


def test_connection_cogs(ctx, database):
    content = ctx.json
    row1 = database.select('''SELECT * FROM cantina_administration.api where token=%s''', (escape(content['api-token']),), 1)
    make_log('test_connection', ctx.remote_addr, content['api-token'], 4, content['api-token'])
    return jsonify({
        "status-code": "200",
        "api-id": row1[0],
        "api-token": escape(content['api-token']),
        "api-name": row1[2],
        "api-desc": row1[3],
        "owner": row1[4],
    })
