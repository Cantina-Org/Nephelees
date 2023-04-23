from flask import redirect


def login_cogs(ctx, database):
    to_redirect = database.select('''SELECT fqdn FROM cantina_administration.domain WHERE name="cerbere"''', number_of_data=1)
    return redirect('http://'+to_redirect[0]+'/auth/nephelees', code=302)
