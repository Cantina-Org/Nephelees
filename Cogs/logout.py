from flask import redirect, url_for, make_response
from Utils.utils import make_log


def logout_cogs(ctx, database):
    make_log('logout', ctx.remote_addr, ctx.cookies.get('userID'), 1, database)
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('userID', '', expires=0)
    return resp
