from shutil import rmtree, copy2
from string import ascii_lowercase
from flask import redirect, url_for, render_template, abort
from random import choices
from os import walk, mkdir, system, remove
from werkzeug.utils import secure_filename
from Utils.utils import make_tarfile, salt_password
from hashlib import sha256


fd, filenames, lastPath = "", "", ""


def file_cogs(ctx, database, dir_path, share_path):
    global filenames, lastPath, fd
    actual_path, lastPath, rand_name = '/', '/', ''
    args = ctx.args
    work_file_in_dir, work_dir = [], []
    git_repo = False
    user_token = ctx.cookies.get('token')

    # Redirection vers la connection si l'utilisateur n'est pas connecté
    if not user_token:
        return redirect(url_for('login'))

    for i in choices(ascii_lowercase, k=10):
        rand_name += i

    row = database.select(f'''SELECT work_Dir, admin, user_name FROM cantina_administration.user WHERE token = %s''',
                          (user_token,), 1)
    if not args.getlist('path'):
        if row[1]:
            for (dirpath, dirnames, filenames) in walk(dir_path):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
        elif not row[1]:
            for (dirpath, dirnames, filenames) in walk(row[0]):
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break

    else:
        actual_path_not_corrected = args.get('path').split("/")
        for i in actual_path_not_corrected:
            if i:
                actual_path += i + '/'
        last_path_1 = actual_path[:-1].split("/")
        for i in range(0, len(last_path_1) - 1):
            if last_path_1[i]:
                lastPath = lastPath + last_path_1[i] + '/'

        if row[1]:
            for (dirpath, dirnames, filenames) in walk(dir_path + '/' + args.get('path')):
                if '.git' in dirnames:
                    git_repo = True
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break
        elif not row[1]:
            for (dirpath, dirnames, filenames) in walk(row[0] + args.get('path')):
                if '.git' in dirnames:
                    git_repo = True
                work_file_in_dir.extend(filenames)
                work_dir.extend(dirnames)
                break

    if not args.get('action') or args.get('action') == 'show':
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=actual_path,
                               lastPath=lastPath, git_repo=git_repo)

    elif args.get('action') == "deleteFile" and args.get('workFile') and args.get('workFile') in filenames:
        if row[1]:
            remove(dir_path + actual_path + secure_filename(args.get('workFile')))
        elif not row[1]:
            remove(row[0] + '/' + actual_path + secure_filename(args.get('workFile')))
        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "createFile" and args.get('workFile'):
        if row[1]:
            fd = open(dir_path + actual_path + secure_filename(args.get('workFile')), 'w')
        elif not row[1]:
            fd = open(row[0] + '/' + args.get('path') + "/" + secure_filename(args.get('workFile')), 'w')

        fd.close()
        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "cloneRepo" and args.get('repoLink'):
        if row[1]:
            system("cd " + dir_path + actual_path + " && git clone " + args.get('repoLink'))
        elif not row[1]:
            system("cd " + row[0] + '/' + args.get('path') + "/ && git clone " + args.get('repoLink'))

        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "pullRepo" and git_repo:
        if row[1]:
            system("cd " + dir_path + args.get('path') + "/ && git pull")
        elif not row[1]:
            system("cd " + row[0] + '/' + args.get('path') + "/ && git pull")

        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "deleteFolder" and args.get('workFile') and args.get('workFile') in work_dir:
        if row[1]:
            rmtree(dir_path + actual_path + "/" + args.get('workFile'))
        elif not row[1]:
            rmtree(row[0] + '/' + actual_path + args.get('workFile'))

        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path)

    elif args.get('action') == "createFolder" and args.get('workFile'):
        if row[1]:
            mkdir(dir_path + actual_path + args.get('workFile'))
        elif not row[1]:
            mkdir(row[0] + '/' + actual_path + args.get('workFile'))
        return render_template("redirect/r-myfile.html", path="/file/?path=" + actual_path, lastPath=lastPath)

    elif args.get('action') == "shareFile" and args.get('workFile') and args.get('loginToShow'):
        if row[1]:
            try:
                copy2(dir_path + actual_path + args.get('workFile'),
                      share_path + '/' + row[2] + '/' + args.get('workFile'))
            except FileNotFoundError:
                mkdir(share_path + '/' + row[2])
                copy2(dir_path + actual_path + args.get('workFile'),
                      share_path + '/' + row[2] + '/' + args.get('workFile'))
            except PermissionError:
                return abort(403)
        elif not row[1]:
            try:
                copy2(row[0] + '/' + actual_path + args.get('workFile'),
                      share_path + row[2] + '/' + args.get('workFile'))
            except FileNotFoundError:
                mkdir(share_path + '/' + row[2])
                copy2(row[0] + '/' + actual_path + args.get('workFile'),
                      share_path + row[2] + '/' + args.get('workFile'))
            except PermissionError:
                return abort(403)
        if args.get('loginToShow') == '0':
            new_salt = sha256().hexdigest()
            salted_password = salt_password(args.get('password'), new_salt, database, ctx, new_password=True)
            database.insert('''INSERT INTO cantina_administration.file_sharing(file_name, file_owner, file_short_name, 
                login_to_show, password, salt) VALUES (%s, %s, %s, %s, %s, %s)''', (args.get('workFile'), row[2],
                                                                                    rand_name, args.get('loginToShow'),
                                                                                    salted_password, new_salt))

        elif args.get('loginToShow') == '1':
            database.insert('''INSERT INTO cantina_administration.file_sharing(file_name, file_owner, file_short_name, 
                login_to_show, password) VALUES (%s, %s, %s, %s, %s)''', (args.get('workFile'), row[2], rand_name,
                                                                          args.get('loginToShow'), salt_password(
                args.get('password'), row[2], ctx, database)))

        return render_template("redirect/r-myfile-clipboardcopy.html", short_name=rand_name,
                               path="/file/?path=" + actual_path)

    elif args.get('action') == "shareFolder" and args.get('workFolder') and args.get('loginToShow'):
        if row[1]:
            try:
                make_tarfile(share_path + '/' + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                             dir_path + actual_path + args.get('workFolder'))
            except FileNotFoundError:
                mkdir(share_path + '/' + row[2])
                make_tarfile(share_path + '/' + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                             dir_path + actual_path + args.get('workFolder'))
            except PermissionError:
                return 403
        elif not row[1]:
            try:
                make_tarfile(share_path + '/' + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                             row[0] + '/' + actual_path + args.get('workFolder'))
            except FileNotFoundError:
                mkdir(share_path + '/' + row[2])
                make_tarfile(share_path + '/' + row[2] + '/' + args.get('workFolder') + '.tar.gz',
                             row[0] + '/' + actual_path + args.get('workFolder'))
            except PermissionError:
                return 403
        database.insert('''INSERT INTO cantina_administration.file_sharing(file_name, file_owner, file_short_name, 
        login_to_show, password) VALUES (%s, %s, %s, %s, %s)''', (args.get('workFolder') + '.tar.gz', row[2], rand_name,
                                                                  args.get('loginToShow'),
                                                                  salt_password(args.get('password'),
                                                                                row[2], database, ctx)))
        return render_template("redirect/r-myfile-clipboardcopy.html", short_name=rand_name,
                               path="/file/?path=" + actual_path)

    else:
        return render_template('myfile.html', dir=work_dir, file=work_file_in_dir, path=args.get('path') + "/",
                               lastPath=lastPath)
