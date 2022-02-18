from content_manager import UseDatabase
from flask import Flask, render_template, request, redirect, url_for, Blueprint, current_app, session

hosp = Blueprint('hosp', __name__, template_folder='templates', static_folder='static')


@hosp.route('/', methods=['GET', 'POST'])
def index():
    rout = {
        '1': url_for('add_patience.index'),
        '8': url_for('attach_otdel.index'),
        '9': url_for('attach_palata.index'),
        '4': url_for('menu_zapros')
        }

    point = request.args.get('point')
    print(f"point={point}")
    if session['user_group'] == "admins":

        res_menu = [
        {"name": "внести нового пациента в бд(admins level)", "url" : "?point=1"},
        {"name": "назначить отделение", "url" : "?point=8"},
        {"name": "назначить палату", "url": "?point=9"},
        # {"name": "главное меню", "url": "?point=4"}
    ]
    else:
        res_menu = [
            # {"name": "внести нового пациента в бд(admins level)", "url": "?point=1"},
            {"name": "назначить отделение", "url": "?point=8"},
            {"name": "назначить палату", "url": "?point=9"},
            # {"name": "главное меню", "url": "?point=4"}
        ]
    if point is None: #reload
        return render_template('hosp_pat_menu.html', menu=res_menu, user_group=session['user_group'])
    else:
        if point == '4':
            return redirect(rout[point])

        if session['user_group'] in current_app.config['access'][point]:
            print("rout[point] = {}".format(rout[point]))
            print("point = {}".format(point))
            return redirect(rout[point])
        else:
            msg = session['user_group'] + " недостаточно прав"
            return render_template('hosp_pat_menu.html', menu=res_menu, user_group=msg)
