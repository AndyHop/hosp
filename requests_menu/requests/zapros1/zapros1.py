import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros1 = Blueprint('zapros1', __name__, template_folder = 'templates', static_folder = 'static')

@zapros1.route('/', methods=['GET','POST'])
def index():
	if session['user_group'] in current_app.config['access']['1']:
		user = session['user_group']
		if 'send' in request.form and request.form['send']=='Отправить':
			doctor = request.form.get('doctor')
			print("!!")
			if doctor:
				with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
					patience = find_employees(cursor, doctor)
				return render_template('zapros1.html', doctor=doctor, patience=patience)
			else:
				with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
					doctors = get_doctors(cursor)
					return render_template('entry.html', doctors=doctors)
		else:
			with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
				doctors = get_doctors(cursor)
				return render_template('entry.html', doctors=doctors)
	else:
		print(session['user_group'])
		return redirect('/menu')


def find_employees(cursor, information):
	SQL = f"""select p.name AS 'name patience', p.hosp_date AS 'diagnose IN', p.receipt_diagnose AS 'receipt_diagnose'
			from hospital.patience p
	 		join doctors d on d.id_doctors = p.uid_attending_doc 
	 		and d.name = '{information}';""" #'Иванов Андрей Касимович'
	cursor.execute(SQL	)
	result = cursor.fetchall()
	res = []
	schema = ['name patience','diagnose IN', 'receipt_diagnose']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

def get_doctors(cursor):
	SQL = "select id_doctors, name from doctors"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['id_doctors', 'name']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res