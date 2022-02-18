import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros3 = Blueprint('zapros3', __name__, template_folder = 'templates', static_folder = 'static')

@zapros3.route('/', methods=['GET','POST'])
def index():
	user = session['user_group']
	if session['user_group'] in current_app.config['access']['2']:
		if 'send' in request.form and request.form['send']=='Отправить':

			year = request.form.get('year')
			print(year)
			with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
				info = show_info(cursor, year)
				return render_template('zapros3.html', info = info)
		else:
			with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
				info = show_years(cursor)
				return render_template('entry3.html', year = info)
	else:
		print(session['user_group'])
		return redirect('/menu')


def show_info(cursor, year: int):
	SQL = f"""Select d.id_doctors, d.name, datediff(d.fin_date, d.start_date)/365 as diff_years, d.uid_myotd from hospital.doctors d 
	Where datediff(current_date(), d.start_date) =  (select Max(datediff(current_date(), d.start_date)) From hospital.doctors d      
	where d.fin_date is not null and year(d.start_date) = {year});"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['id_doctors','name', 'diff_years', 'uid_myotd']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

def show_years(cursor):
	SQL = f"""select YEAR(start_date) number from doctors"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	tmp = []
	[tmp.append(x) for x in result if x not in tmp]
	res = []
	schema = ['number']
	for blank in tmp:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res