from content_manager import UseDatabase
from flask import Flask, render_template, request, redirect, url_for, Blueprint, current_app, session

attach_otdel = Blueprint('attach_otdel', __name__, template_folder='templates', static_folder='static')
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


@attach_otdel.route('/', methods=['GET', 'POST'])
def index():
    if session['user_group'] not in current_app.config['access']['8']:
        return redirect(url_for('menu_zapros'))
    user = session['user_group']
    init_cart()
    with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
        list_of_orders = show_orders(cursor)
        services = get_services(cursor)
        point = request.args.get('point')
        print(f"point={point}")

        if 'search' in request.form and request.form['search'] == "получить":
            hosp_date = request.form.get('hosp_date')
            print(hosp_date)
            patience = get_patience(cursor, hosp_date)
            print(patience)
            return render_template("att_otdl_menu.html", patience = patience)

        elif 'conf' in request.form and request.form['conf'] == "назначить отделение":
            print("назначить отделение")
            print(request.form)
            pat_id = request.form.get('pat_id')
            pat = get_specific_patience(cursor, pat_id)
            otdel_info = get_services(cursor)
            return render_template("attach.html", otdel_info = otdel_info, pat = pat, pati_id = pat_id)

        elif 'confirm' in request.form and request.form['confirm'] == "выбрать":
            print(request.form)
            id_otdel = request.form.get('id_otdel')
            print(f"id_otdel = {id_otdel}")
            pat_id = request.form.get('pat_id')
            session['cart'] = upd_uid_otdel(id_otdel, pat_id)
            print("session['cart']", session['cart'])
            if session['user_group'] in current_app.config['access']['9']:
                return redirect(url_for('attach_palata.index'))
            else:
                return render_template("search.html", top="выберите подходящее отделение ")
        else:
            return render_template("search.html", top="выберите подходящее отделение ")


@attach_otdel.route('attach', methods=['GET', 'POST'])
def attach():
    print("@@@@@@@@@")
    if session['user_group'] not in current_app.config['access']['8']:
        return redirect(url_for('menu_zapros'))
    user = session['user_group']
    init_cart()
    with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
        list_of_orders = show_orders(cursor)
        services = get_services(cursor)
        point = request.args.get('point')
        print(f"point={point}")

        if 'new_order' in request.form and request.form['new_order'] == "новый заказ":
            return render_template("def.html")


        else:
            return render_template("att_otdl_menu.html", menu = list_of_orders,
                                   top = "вы можете создать новый или отредактировать уже созданный заказ")


def check_pat_sessoin(pat_id, id_otdel):
    for pat in session['cart']:
        if pat['pat_id']==pat_id:
            pat['id_otdel'] = id_otdel
            return True
        else:
            pass
    return False

def upd_uid_otdel(id_otdel, pat_id):

    flag = check_pat_sessoin(pat_id, id_otdel)

    if flag == False:
        session['cart']+=[{
        'id_otdel': id_otdel,
        'pat_id':pat_id
        }]
    return session['cart']

def get_patience(cursor, date):
    cursor.execute(f"select id_patience, name, birthday, receipt_diagnose, receipt_date from patience "
                   f"where hosp_date = '{date}'"
                   f"and uid_palata is NULL;")
    result = cursor.fetchall()
    res = []
    schema = ['id_patience', 'name', 'birthday', 'receipt_diagnose', 'receipt_date']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res

def get_specific_patience(cursor, pat_id):
    cursor.execute(f"select id_patience, name, birthday, receipt_diagnose, receipt_date, hosp_date from patience "
                   f"where id_patience = {pat_id} and uid_palata is NULL;")
    result = cursor.fetchall()
    res = []
    schema = ['id_patience', 'name', 'birthday', 'receipt_diagnose', 'receipt_date', 'hosp_date']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res

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
    cursor.execute("select otdelenie.number, otdelenie.id_otdelenie, otdelenie.name, "
                   "count(*) palat, sum(capacity) cap from palata "
                   "join otdelenie on otdelenie.id_otdelenie = palata.uid_otdelenie "
                   "group by uid_otdelenie order by id_otdelenie asc;")

    otdel = cursor.fetchall()

    res = []
    schema = ['number','id_otdelenie', 'name', 'palat', 'cap']
    for blank in otdel:
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


