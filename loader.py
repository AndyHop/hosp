import json
from requests_menu.requests.zapros1.zapros1 import zapros1
from requests_menu.requests.zapros3.zapros3 import zapros3
from requests_menu.requests.zapros4.zapros4 import zapros4
from requests_menu.requests.zapros5.zapros5 import zapros5
from requests_menu.requests.zapros6.zapros6 import zapros6
from requests_menu.requests.zapros2.zapros2 import zapros2
from attach_doctor.attach_doctor import attach_doctor
from hospitalization.adding_patience.add_patience import add_patience
from hospitalization.attach_palata.attach_palata import attach_palata
from hospitalization.attach_otdel.attach_otdel import attach_otdel
from hospitalization.hosp import hosp
from auth.auth import auth
from logout import delete_cookie
from requests_menu.req_menu import req_menu
from report.report import report
from cart.cart import cart


with open('data_files/main_menu_access.json') as f:
    main_menu_access = json.load(f)

def loader(config, app):
    with open('data_files/dbconfig.json', 'r') as f:
        dbconfig = json.load(f)

    with open('data_files/menu.json', 'r') as f:
        menu = json.load(f)

    config['dbconfig'] = dbconfig

    with open('data_files/secret_key.json', 'r') as f:
        app_config = json.load(f)

    config['SECRET_KEY'] = app_config['secret_key']

    with open('data_files/menu.json', encoding='utf-8') as f:
        menu_items = json.load(f)

    with open('data_files/access.json') as f:
        query_access_items = json.load(f)

    config['access'] = query_access_items

    app.register_blueprint(report, url_prefix='/report')
    app.register_blueprint(zapros1, url_prefix='/zapros1')
    app.register_blueprint(zapros2, url_prefix='/zapros2')
    app.register_blueprint(zapros3, url_prefix='/zapros3')
    app.register_blueprint(zapros4, url_prefix='/zapros4')
    app.register_blueprint(zapros5, url_prefix='/zapros5')
    app.register_blueprint(zapros6, url_prefix='/zapros6')
    app.register_blueprint(req_menu, url_prefix='/req_menu')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(delete_cookie, url_prefix='/delete-cookie')
    app.register_blueprint(cart, url_prefix='/cart')
    app.register_blueprint(hosp, url_prefix='/hosp')
    app.register_blueprint(add_patience, url_prefix='/add_patience')
    app.register_blueprint(attach_palata, url_prefix='/attach_palata')
    app.register_blueprint(attach_otdel, url_prefix='/attach_otdel')
    app.register_blueprint(attach_doctor, url_prefix='/attach_doctor')
    return menu_items, app

def res_menu_creater(user):
    res_menu = [

            {"name": "Запросы", "url": "?point=2"},
            {"name": "госпитализация", "url": "?point=8"},
            {"name": "назначить врача", "url": "?point=9"}
        ]
    new_menu = []
    #
    #

    if user == "guest":
        new_menu.append({"name": "вход", "url": "?point=1"})
    else:
        new_menu.append({"name": "Выход", "url": "?point=5"})

    for row in res_menu:
        ind = res_menu.index(row) + 1
        # print("строчка" , ind, row)
        try:
            tmp = main_menu_access[str(ind)]
        except:
            # print(f"row dont exist {row}")
            continue
        if user in main_menu_access[str(ind)]:

            new_menu.append(row)


    # print("new_menu = " + str(new_menu))
    return new_menu