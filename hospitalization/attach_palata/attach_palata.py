from content_manager import UseDatabase
from flask import Flask, render_template, request, redirect, url_for, Blueprint, current_app, session

attach_palata = Blueprint('attach_palata', __name__, template_folder='templates', static_folder='static')

session_order = {
    'cl_name': "",
    'session_order_id': 0
}
order_comp = {
    'session_order_id': 0,
    'service_id': 0,
    'amount': 0
}


@attach_palata.route('/', methods=['GET', 'POST'])
def index():
    if session['user_group'] not in current_app.config['access']['8']:
        return redirect(url_for('menu_zapros'))
    user = session['user_group']

    with UseDatabase(current_app.config['dbconfig'][user]) as cursor:
        point = request.args.get('point')
        print(f"point={point}")

        if 'search' in request.form and request.form['search'] == "получить":
            print('search', request.form)
            hosp_date = request.form.get('hosp_date')
            print(hosp_date)
            patience = get_patience(cursor, hosp_date)
            print(patience)
            return render_template("att_otdl_menu.html", patience = patience)

        elif 'conf' in request.form and request.form['conf'] == "перейти к палатам":
            print('conf', request.form)
            id_otdel = request.form.get('id_otdel')
            pat_id = request.form.get('id_pat')
            pat = get_specific_patience(cursor, pat_id)
            otdel_info = get_services(cursor, id_otdel)
            print("pat",pat)
            return render_template("palatas.html", otdel_info = otdel_info, id_otdel = id_otdel, pati_id = pat_id, pat=pat[0])

        elif 'confirm' in request.form and request.form['confirm'] == "выбрать":
            print('confirm' , request.form)
            id_palat = request.form.get('id_palat')
            pat_id = request.form.get('pat_id')
            session['cart'] = upd_uid_otdel(id_palat, pat_id, "del")
            print(id_palat, pat_id, "@@@@@@" )
            cursor.execute(f"update patience set uid_palata = {id_palat} where id_patience = {pat_id};")
            return render_template("search.html", top="выберите подходящее отделение ")

        else:
            print("else")
            print(request.form)
            pat_list = get_ready_pat(cursor)
            top = "пациенты готовые к распределению в палаты: "
            if len(pat_list) == 0:
                print("pat_list",pat_list)
                top = "не найдено ни одного пациента в текущей сессии"
            return render_template("pat_palata.html", pat_list = pat_list, top = top)




def check_pat_sessoin(pat_id, id_otdel):
    for pat in session['cart']:
        if pat['pat_id']==pat_id:
            pat['id_otdel'] = id_otdel
        else:
            return False
    return True

def upd_uid_otdel(id_otdel, pat_id, state):

    if state == "del":
        for pat in session['cart']:
            if pat['pat_id'] == pat_id:
                indx = session['cart'].index(pat)
                del session['cart'][indx]
    return session['cart']



def get_ready_pat(cursor):
    pat = []
    try:
        for p in session['cart']:
            print(p['pat_id'], p['id_otdel'])
            cursor.execute(f"select id_patience, name, birthday, receipt_diagnose, receipt_date from patience "
                           f"where id_patience = {p['pat_id']}")
            res = cursor.fetchone()
            tmp = list(res)
            # print(tmp, "tmp")
            cursor.execute(f"select name, id_otdelenie from otdelenie where id_otdelenie = {p['id_otdel']};")
            otdl = cursor.fetchone()
            tmp_otdl = list(otdl)
            tmp += tmp_otdl
            tupletmp = tuple(tmp)
            pat.append(tupletmp)
    except:
        res = []
        print("eternal server error")
        return res
    print(pat)
    res = []
    schema = ['id_patience', 'name', 'birthday', 'receipt_diagnose', 'receipt_date', 'otdel', 'id_otdelenie']
    for blank in pat:
        res.append(dict(zip(schema, blank)))
    return res





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

def get_services(cursor, id_otdel):
    sql2 = "select count(*) full, palata.capacity,  uid_palata palat_id from patience join palata on patience.uid_palata = palata.idpalata  where uid_palata is not null group by uid_palata;"
    big_list = []

    sql = f"select o.id_otdelenie, o.name, p.idpalata, p.plt_num, p.capacity, p.category from otdelenie o left join palata p on p.uid_otdelenie = o.id_otdelenie where id_otdelenie = {id_otdel};"
    cursor.execute(sql)
    result = cursor.fetchall()
    for row in result:
        tmp = row_tmp = list(row)
        print(row[2])
        cursor.execute(f"select count(*) from patience where uid_palata = {row[2]};")
        row_tmp += list(cursor.fetchone())
        tmp = tuple(row_tmp)
        big_list.append(tmp)

    res = []
    schema = ['id_otdelenie', 'name', 'idpalata', 'plt_num', 'capacity', 'category', 'free']
    for blank in big_list:
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
