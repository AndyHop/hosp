import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros4 = Blueprint('zapros4', __name__, template_folder = 'templates', static_folder = 'static')

@zapros4.route('/', methods=['GET','POST'])
def index():
	if session['user_group'] in current_app.config['access']['2']:
		if 'send' in request.form and request.form['send']=='Отправить':
			user = session['user_group']
			with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
				info = show_info(cursor)
				return render_template('zapros4.html', info = info)
		else:
				return render_template('entry4.html')
	else:
		print(session['user_group'])
		return redirect('/menu')


def show_info(cursor):
	SQL = f"""select p.*
from hospital.patience p
where p.receipt_date = (
	select min(receipt_date)
    from patience
);"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['idpatience', 'name', 'birthday', 'address', 'receipt_date', 'receipt_diagnose', 'discharge_date', 'discharge_diagnose', 'uid_palata', 'uid_attending_doc', 'hosp_date']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

