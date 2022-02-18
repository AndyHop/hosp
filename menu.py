from flask import Flask, render_template,request,redirect, url_for, session
from loader import loader, res_menu_creater
import json
app = Flask(__name__)


menu_items, app = loader(app.config, app)


@app.route('/menu/', methods=['GET', 'POST'])
def menu_zapros():
    if 'user_group' not in session:
        session['user_group'] = 'guest'

    rout = {
        '1': url_for('auth.index'),
        '2': url_for('req_menu.index'),
        # '3': url_for('cart.index'),
        '5': url_for('delete_cookie.del_cookie'),
        # '6': url_for('report.index'),
        '8': url_for('hosp.index'),
        '9': url_for('attach_doctor.index')
    }

    point = request.args.get('point')
    print(f"point={point}")

    try:
        print("session['user_group'] = {}".format(session['user_group']))
    except:
        print("error")


    res_menu = res_menu_creater(session['user_group'])

    if point is None: #reload
        return render_template('menu.html', menu=res_menu, user_group=session['user_group'])
    else:
        print("rout[point] = {}".format(rout[point]))
        print("point = {}".format(point))
        return redirect(rout[point])




@app.route("/exit")
def exit_page():
    session.clear()
    return "Goodbye, world!"
    
@app.route('/')
def rdrc():
    return redirect('/menu')

app.run(debug = True, port = 5007)



