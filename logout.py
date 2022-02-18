from flask import request, make_response, Blueprint, session, redirect, render_template

delete_cookie = Blueprint('delete_cookie', __name__)


@delete_cookie.route('/')
def del_cookie():
    if request.cookies.get("session") is None or session['user_group'] == 'guest':
        return redirect('/menu')
    res = make_response(render_template('logout.html'))
    sescart = []
    try:
        sescart = session['cart']
    except:
        print("nothing to save")
    res.set_cookie('session', request.cookies.get("session"), max_age=-1)
    # session.clear()
    print(sescart)
    session["user_group"] = 'guest'
    session["cart"] = sescart
    return res
