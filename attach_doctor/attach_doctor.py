from content_manager import UseDatabase
from flask import Flask, render_template, request, redirect, url_for, Blueprint, current_app, session

attach_doctor = Blueprint('attach_doctor', __name__, template_folder='templates', static_folder='static')
otdels = {
    "head_terapy": 2,
    "head_surgery": 0,

}
session_order = {
    'cl_name': "",
    'session_order_id': 0
}
order_comp = {
    'session_order_id': 0,
    'service_id': 0,
    'amount': 0
}


@attach_doctor.route('/', methods=['GET', 'POST'])
def index():
    if session['user_group'] not in current_app.config['access']['9']:
        return redirect(url_for('menu_zapros'))
    user = session['user_group']

    if 'conf' in request.form and request.form['conf'] == "назначить врача":
        pat_id = request.form.get('pat_id')
        otdel_id = request.form.get('otdel_id')
        with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
            doctors = show_info(cursor, otdel_id)
            patience = get_specific_patience(cursor, pat_id)
            print(patience)
        return render_template("def_show.html",doctors = doctors, pat = patience)

    elif 'confirm' in request.form and request.form['confirm'] == "Отправить":
        print(request.form)
        pat_id = request.form.get('patient_id')
        doctor = request.form.get('doctor')
        print(f"pat_id= {pat_id}, doctor = {doctor} ")
        with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
            update_data(cursor, pat_id, doctor)
        return render_template("deff.html", info = "пациент распределен")

    else:
        otdel = get_otdel(user)
        with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
            patience = get_patience(cursor, otdel)
            # doctors = show_info(cursor, otdel)
        return render_template("show.html",patience = patience, otdel = otdel, top = "списки пациентов у которых нет назначенного врача, вашего отделения")

def get_otdel(user):
    return otdels[user]


def update_data(cursor, pat_id, doc_id):
    cursor.execute(f"update patience set uid_attending_doc = {doc_id} where id_patience = {pat_id};")




def get_specific_patience(cursor, pat_id):
    cursor.execute(f"select id_patience, name, birthday, receipt_diagnose, receipt_date, hosp_date from patience "
                   f"where id_patience = {pat_id};")
    result = cursor.fetchall()
    res = []
    schema = ['id_patience', 'name', 'birthday', 'receipt_diagnose', 'receipt_date', 'hosp_date']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res

def show_info(cursor, otdel):
	SQL = f"""select d.*
		from doctors d
		left join patience p on p.uid_attending_doc = d.id_doctors
		where p.id_patience is null
		and d.uid_myotd = {otdel};"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['id_doctors','name', 'start_date', 'fin_date', 'uid_myotd']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

def create_new_session_order(client, db_ordr_id):
    session['cart']+=[{
    'DB_ordr_id': db_ordr_id,
    'cl_name': client,
    'session_order_id': len(session['cart']) + 1,
    'order_comp': []
}]
    return session['cart'], len(session['cart'])


def get_patience(cursor, otdel):
    cursor.execute(f"select id_patience, name, birthday, receipt_diagnose, receipt_date from patience "
                   f"left join palata on patience.uid_palata = palata.idpalata where uid_attending_doc is null and uid_palata is not null and palata.uid_otdelenie = {otdel};")
    result = cursor.fetchall()
    res = []
    schema = ['id_patience', 'name', 'birthday', 'receipt_diagnose', 'receipt_date']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res


def create_old_session_order(cursor,db_ordr_id):

    cursor.execute("select client from orders where id = {};".format(db_ordr_id))
    name = cursor.fetchone()[0]
    session['cart'] += [{
        'DB_ordr_id': db_ordr_id,
        'cl_name': name,
        'session_order_id': len(session['cart']) + 1,
        'order_comp': []
    }]
    return session['cart'], len(session['cart'])

def update_comp(cursor, db_ordr_id):
    cursor.execute("select * from cart where order_id = {}".format(db_ordr_id))
    result = cursor.fetchall()
    for row in result:
        # print("row = {}".format(row))
        for i in range(0, int(row[2])):
            add_to_cart(len(session['cart']), str(row[1]))
    return session['cart']

def init_cart():
    if 'cart' not in session:
        session['cart'] = []


def show_orders(cursor):
    cursor.execute("select * from orders")
    result = cursor.fetchall()
    res = []
    schema = ['id', 'client', 'total_cost', 'created_at', 'amount']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res


def get_order_data(ordr_id): # todo search in session
    ordr_id -= 1
    result = session['cart'][ordr_id]['order_comp']
    # print(f"result={result}")
    res = []
    schema = ['session_order_id',  'service_id', 'amount']

        # print(f"result={result}")
        # print(f"blank={blank}")
        # res.append(dict(zip(schema, blank)))
    return result

def get_services(cursor):
    cursor.execute("select * from services")
    result = cursor.fetchall()
    res = []
    schema = ['id', 'name', 'cost']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res


def delete_from_cart(ordr_id, service_id):
    # order_comp = {
    #     'session_order_id': ordr_id,
    #     'service_id': service_id,
    #     'amount': 1
    # }
    flag = 0
    ordr_id -= 1  # list index starts with 0
    # print(f"session['cart'][ordr_id] = {session['cart'][ordr_id]['order_comp']}")
    for comp in session['cart'][ordr_id]['order_comp']:
        if service_id == comp['service_id']:
            comp['amount'] -= 1
            if comp['amount'] == 0:
                indx = session['cart'][ordr_id]['order_comp'].index(comp)
                del session['cart'][ordr_id]['order_comp'][indx]
    return session['cart']

def add_to_cart(ordr_id, service_id):
    # order_comp = {
    #     'session_order_id': ordr_id,
    #     'service_id': service_id,
    #     'amount': 1
    # }
    flag = 0
    ordr_id -= 1  # list index starts with 0
    # print(f"session['cart'][ordr_id] = {session['cart'][ordr_id]['order_comp']}")
    for comp in session['cart'][ordr_id]['order_comp']:
        if service_id == comp['service_id']:
            comp['amount'] += 1
            flag = 1
    if flag == 0:
        session['cart'][ordr_id]['order_comp'] += [{
            'session_order_id': ordr_id,
            'service_id': service_id,
            'amount': 1
        }]
    return session['cart']


def get_total(data, cursor):
    total = 0
    for row in data:
        # print(row)
        cursor.execute("select cost from services where id ={};".format(row['service_id']))
        res = cursor.fetchone()
        total += int(res[0]) * row["amount"]
    return total


def save_basket(cursor, ordr_id):
    ordr_id -= 1
    cl_name = session['cart'][ordr_id]['cl_name']
    data = get_order_data(ordr_id)
    total = get_total(data, cursor)
    true_id = session['cart'][ordr_id]['DB_ordr_id']
    print(session['cart'][ordr_id]['DB_ordr_id'])
    if int(session['cart'][ordr_id]['DB_ordr_id']) > -1:
        cursor.execute("update orders set total_cost = {} where id = {};".format(total, session['cart'][ordr_id]['DB_ordr_id']))
        cursor.execute("delete from cart where order_id = {}".format(session['cart'][ordr_id]['DB_ordr_id']))
    else:
        cursor.execute(f"insert into orders(client, total_cost, created_at) values(\"{cl_name}\", {total}, current_date());")
        true_id = cursor.lastrowid
    for row in data:
        print(f"row= {row}")
        cursor.execute(f"insert into cart(order_id, service_id, amount) values({true_id},{row['service_id']},{row['amount']});")
    print("!!")

    session['cart'] = []
    return cl_name





