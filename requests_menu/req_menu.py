from content_manager import UseDatabase
from flask import Flask, render_template, request, redirect, url_for, Blueprint, current_app, session

req_menu = Blueprint('req_menu', __name__, template_folder='templates', static_folder='static')


@req_menu.route('/', methods=['GET', 'POST'])
def index():
    rout = {
        '1': url_for('zapros1.index'),
        '4': url_for('zapros2.index'),
        '5': url_for('zapros3.index'),
        # '6': url_for('zapros4.index'),
        '7': url_for('zapros5.index'),
        '10': url_for('zapros6.index'),
        '3': url_for('menu_zapros')
    }

    point = request.args.get('point')
    print(f"point={point}")

    res_menu = [
        {"name": "посмотреть назначенных пациентов", "url" : "?point=1"},
        {"name": "информация по отделениям", "url" : "?point=4"},
        {"name": "информация о сотрудниках", "url": "?point=5"},
        # {"name": "requets 4", "url": "?point=6"},
        {"name": "врачи без прикрепленных пациентов", "url": "?point=7"},
        {"name": "врачи к которым поступали пациенты", "url": "?point=10"},
        # {"name": "главное меню", "url": "?point=3"}
    ]

    if point is None: #reload
        return render_template('req_menu.html', menu=res_menu,  user_group=session['user_group'])
    else:
        if point == '3':
            return redirect(rout[point])

        if session['user_group'] in current_app.config['access'][point]:
            print("rout[point] = {}".format(rout[point]))
            print("point = {}".format(point))
            return redirect(rout[point])
        else:
            msg = session['user_group'] + " недостаточно прав"
            return render_template('req_menu.html', menu=res_menu, user_group=msg)









