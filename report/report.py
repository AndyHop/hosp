import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


report = Blueprint('report', __name__, template_folder='templates', static_folder='static')


@report.route('/', methods=['GET', 'POST'])
def index():
    if (session['user_group'] in current_app.config['access']['9']):
        if 'send' in request.form and request.form['send'] == 'send':
            year = request.form.get('year')
            month = request.form.get('month')
            user = session['user_group']
            print('DELAEM OT4ET', (year,))
            if year:
                with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
                    rows, status = call_proc(cursor, year)
                return render_template('result_report.html', year=year, ships=rows, status=status)
            else:
                return render_template('enter_report.html')
        else:
            return render_template('enter_report.html')
    elif session['user_group'] == 'guest':
        print(session['user_group'])
        return redirect('/auth')
    else:
        print(session['user_group'])
        return redirect('/menu')


def call_proc(cursor, year):
    args = (year,)
    status = "enable"
    try:
        cursor.callproc('ship_reported', args=args)
    except:
        print("res call_proc")
        status = "execute command denied"

    SQL = f""" SELECT * FROM report1;"""
    cursor.execute(SQL)
    result = cursor.fetchall()
    res = []
    schema = ['t_month', 't_type', 't_amount']
    for blank in result:
        print(blank)
        res.append(dict(zip(schema, blank)))
    return res, status