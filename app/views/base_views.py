from flask import render_template, request, redirect, url_for, abort, Blueprint, flash

from app import limiter
from app.controllers.task_controller import get_task, check_flag, get_all_tasks
from app.controllers.user_controller import add_user, check_user, get_user_scores, get_user, get_user_by_id, get_all_groups
from app.login_tools import login_required, get_base_data, login_user, logout_user
from app.views import LogoutMessage
from app.forms import LoginForm, RegisterForm

view = Blueprint('view', __name__, static_folder='static', template_folder='templates')


@view.route('/')
def index():
    context = get_base_data()
    return render_template('index.html', **context)


@view.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        del form['csrf_token']
        user = check_user(**form.data)
        if user is None:
            flash('Неправильный логин или пароль')
            return render_template('login.html', form=form)
        if not user.active:
            flash("Пользователь неактивен")
            return render_template('login.html', form=form)
        else:
            login_user(user)
            return redirect(url_for('contest_view.list_contests'))
    else:
        return render_template('login.html', form=form)


@view.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    context = dict(form=form)
    if form.validate_on_submit():
        b = form.data
        del b['confirm']
        del b['csrf_token']
        print(b)
        flag = add_user(b)
        if flag:
            # login_user(get_user(form.login.data))
            return redirect('/login')
        else:
            flash('Произошла ошибка!Напишите Николаю или Ивану о ней!!!')
            return redirect('/register')
    else:
        return render_template('register.html', **context)


# @view.route('/tasks')
# @login_required
# def get_tasks():
#     context = get_base_data()
#     task_map = get_all_tasks()
#     if task_map is None:
#         task_map = {"No task": []}
#     context.update(task_map=task_map)
#     return render_template('tasks.html', **context)


@view.route('/task/<_id>', methods=['POST', 'GET'])
@limiter.limit("1 per second")
@login_required
def get_task_page(_id):
    context = get_base_data()
    task = get_task(_id)
    if not task or not task['active']:
        abort(404)
    if request.method == 'GET':
        context.update(task)
        return render_template('task_page.html', **context)
    else:
        usr_flag = request.form['flag']
        message = check_flag(_id, context['u_id'], usr_flag)
        context = get_base_data()
        context.update(message=message)
        return render_template('message.html', **context)


@view.route('/logout')
def logout():
    logout_user()
    flash(LogoutMessage)
    return redirect(url_for('view.index'))


@view.route('/score')
def scoreboard(group_id=None):
    context = get_base_data()
    group_id = request.args.get("group_id")
    context.update(teams=get_user_scores(group_id=group_id))
    return render_template('scores.html', **context)


@view.route('/telegram')
def telegram():
    return "https://telegram.me/joinchat/BC2xhwdCtCCAQ7cbHymaSw"


@view.route('/user/<user_id>')
def user_view(user_id):
    context = get_base_data()
    user = get_user_by_id(user_id)
    context['user'] = user
    return render_template('user_page.html', **context)


@view.route('/report')
def report_view():
    return render_template('report.html')


@view.route('/groups')
def groups_view():
    context = get_base_data()
    context['groups'] = get_all_groups()
    return render_template("groups.html", **context)
