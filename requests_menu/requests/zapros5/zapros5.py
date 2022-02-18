import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros5 = Blueprint('zapros5', __name__, template_folder = 'templates', static_folder = 'static')

@zapros5.route('/', methods=['GET','POST'])
def index():
	user = session['user_group']
	if session['user_group'] in current_app.config['access']['2']:
		with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
			if 'send' in request.form and request.form['send']=='Отправить':
				otdel_id = request.form.get('id_otdel')
				# otdel_id = 1
				info = show_info(cursor, int(otdel_id))
				cursor.close()
				return render_template('zapros5.html', info = info)
			else:
				info = show_otdels(cursor)
				cursor.close()
				return render_template('entry5.html', info= info)
	else:
		print(session['user_group'])
		return redirect('/menu')


def show_info(cursor, otdel_id: int):
	SQL = f"""select d.*, otdelenie.name otdname
		from doctors d
		left join patience p on p.uid_attending_doc = d.id_doctors
		join otdelenie on d.uid_myotd = otdelenie.id_otdelenie
		where p.id_patience is null
		and d.uid_myotd = {otdel_id};"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	cursor.close()
	res = []
	schema = ['id_doctors','name', 'start_date', 'fin_date', 'uid_myotd', 'otdname']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res


def show_otdels(cursor):
	SQL = f"""select id_otdelenie, number, name from otdelenie;"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	cursor.close()
	res = []
	schema = ['id_otdelenie','number', 'name']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

