from content_manager import UseDatabase
from flask import Flask, render_template, request, redirect, url_for, Blueprint, current_app, session

add_patience = Blueprint('add_patience', __name__, template_folder='templates', static_folder='static')
# admin - can truncate table cart
# employ - can add  to cart and delete from it some stuff
# buton new order generate another order
# hm? btw employ can do this: in cart menu there are orders, every order can be edit by adding or deleting stuff
# admin - can delete specific order
session_order = {
    'cl_name': "",
    'session_order_id': 0
}
order_comp = {
    'session_order_id': 0,
    'service_id': 0,
    'amount': 0
}


@add_patience.route('/', methods=['GET', 'POST'])
def index():
    if session['user_group'] not in current_app.config['access']['8']:
        return redirect(url_for('menu_zapros'))
    user = session['user_group']

    if 'new_order' in request.form and request.form['new_order'] == "новый пациент":
        print("request.form['new_order']")
        # id_pat = request.form.get('id_pat')
        cl_name = request.form.get('cl_name')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        receipt_date = request.form.get('receipt_date')
        receipt_diagnose = request.form.get('receipt_diagnose')
        hosp_date = request.form.get('hosp_date')

        SQL = f"""insert into patience(name, pass_data, birthday, address, receipt_date, receipt_diagnose, hosp_date) 
            values('{cl_name}', 0, '{birthday}', '{address}', '{receipt_date}', '{receipt_diagnose}', '{hosp_date}');"""
        with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
            cursor.execute(SQL)

        return render_template("def.html", info=f"клиент {cl_name} успешно зарегистрирован")

    else:
        return render_template("add_patience.html", top = "создание пациента при госпитализации(заполняется до основных БП)")


def create_new_session_order(client, db_ordr_id):
    session['cart']+=[{
    'DB_ordr_id': db_ordr_id,
    'cl_name': client,
    'session_order_id': len(session['cart']) + 1,
    'order_comp': []
}]
    return session['cart'], len(session['cart'])


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
