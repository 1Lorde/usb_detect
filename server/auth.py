from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Перевірте введені дані та спробуйте ще раз.', category='error')
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.dashboard'))


@auth.route('/change_password')
def change_password():
    return render_template('change_password.html', username=current_user.username)


@auth.route('/change_password', methods=['POST'])
def change_password_post():
    username = request.form.get('username')
    prev_password = request.form.get('prev_password')
    new_password = request.form.get('new_password')

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, prev_password):
        flash('Введені дані некоректні.', category='error')
        return redirect(url_for('auth.change_password'))

    user.password = generate_password_hash(new_password, method='sha256')
    # add the new user to the database
    db.session.merge(user)
    db.session.commit()
    flash('Пароль оновлено.', category='success')

    return redirect(url_for('auth.change_password'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
