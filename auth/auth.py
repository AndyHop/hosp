from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, session, current_app

auth=Blueprint('auth',__name__,template_folder = 'templates',  static_folder = 'static')

@auth.route('/',methods=['GET','POST'])
def index():
    if 'send' in request.form and request.form['send'] == 'auth':
        result = []
        print("!")
        login = request.form.get('login')
        password = request.form.get('password')
        user = session['user_group']

        print("log = {}, pass = {}, user = {}".format(login, password, user))

        if login and password:
            with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
                cursor.execute(
                    f"""SELECT role_name FROM users WHERE user_name='{login}'
                    AND user_pass='{password}'"""
                )

                schema = ['user_group']
                for con in cursor.fetchall():
                    result.append(dict(zip(schema, con)))

            if len(result) > 0:
                session['user_group'] = result[0]['user_group']
                print(session['user_group'])
                return redirect('/menu/')
            else:
                return render_template('auth.html', message="wrong username and password pair")
        else:
            return render_template('auth.html',  message="invalid username and password pair")

    else:
        print("!")
        return render_template('auth.html',  message="")

