import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros2 = Blueprint('zapros2', __name__, template_folder = 'templates', static_folder = 'static')

@zapros2.route('/', methods=['GET','POST'])
def index():
	print(current_app.config['access']['2'])
	if session['user_group'] in current_app.config['access']['2']:
		user = session['user_group']
		with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
			info = show_info(cursor)
			return render_template('zapros2.html', info = info)
	else:
		print(session['user_group'])
		return redirect('/menu')


def show_info(cursor):
	SQL = f"""select o.number, o.name AS 'Отделение', d.name AS 'Заведующий', SUM(p.capacity) AS 'Вместимость'
		from hospital.otdelenie o
		join doctors d on o.uid_my_doc = d.id_doctors
    	join palata p on p.uid_otdelenie = o.id_otdelenie
		group by o.id_otdelenie;"""
	cursor.execute(SQL	)
	result = cursor.fetchall()
	res = []
	schema = ['number','Отделение', 'Заведующий', 'Вместимость']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

