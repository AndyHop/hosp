import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros6 = Blueprint('zapros6', __name__, template_folder = 'templates', static_folder = 'static')

@zapros6.route('/', methods=['GET','POST'])
def index():
	if session['user_group'] in current_app.config['access']['1']:
		user = session['user_group']
		if 'send' in request.form and request.form['send']=='Отправить':
			year = request.form.get('year')
			month = request.form.get('month')
			print("!!")
			if int(year) and int(month):
				with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
					doctors = find_employees(cursor, year, month)
				return render_template('zapros6.html', year=year, month=month, doctors=doctors)
			else:
				return render_template('entry6.html')
		else:
			return render_template('entry6.html')
	else:
		print(session['user_group'])
		return redirect('/menu')


def find_employees(cursor, year, month):
	SQL = f"""select name
from hospital.doctors d left join (
	select	 d.id_doctors as id
	from hospital.doctors d
		left join patience p on p.uid_attending_doc = d.id_doctors and month(p.receipt_date) = {month} and year(p.receipt_date) = {year}
	where p.id_patience is not null
) as tmp on d.id_doctors = tmp.id 
where tmp.id is NULL;""" #
	cursor.execute(SQL	)
	result = cursor.fetchall()
	res = []
	schema = ['name']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res
