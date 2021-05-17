from sqlite3 import IntegrityError

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from forms import NewComputerForm
from models import Computer
from server import create_app, db
from server.forms import NewDeviceForm
from server.models import Event, Device
from server.tables import EventTable
from tables import ComputerTable, DeviceTable
from utils import get_stats

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dashboard')
@login_required
def dashboard():
    events = Event.query.order_by(Event.created_at.desc()).all()

    if len(events) == 0:
        return render_template('dashboard.html',
                               stats=get_stats(),
                               table='<p class="subtitle is-italic has-text-dark has-text-centered" '
                                     'style="padding:20px;">'
                                     'Подій не знайдено</p>')

    table = EventTable(events)
    return render_template('dashboard.html', table=table, stats=get_stats())


@main.route('/devices/add', methods=['GET', 'POST'])
@login_required
def add_device():
    form = NewDeviceForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            created_device = Device(serial=form.serial.data, name=form.name.data)

            db.session.add(created_device)
            try:
                db.session.commit()
                flash('Пристрій успішно додано.', category='success')
                return redirect(url_for('main.dashboard'))
            except IntegrityError:
                db.session.rollback()
                flash('Пристрій з таким серійним номером вже існує.', category='error')

            return redirect(url_for('main.dashboard'))
        else:
            flash('Пристрій не додано, необхідні поля пусті.', category='warning')
    return render_template('device.html', form=form, header="Реєстрація пристрою")


@main.route('/devices/<device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()

    if request.method == 'POST':
        form = NewDeviceForm()
        if form.validate_on_submit():
            device.name = form.name.data
            device.serial = form.serial.data
            db.session.merge(device)
            try:
                db.session.commit()
                flash('Інформацію про пристрій успішно оновлено.', category='success')
                return redirect(url_for('main.devices'))
            except IntegrityError:
                db.session.rollback()
                flash('При оновленні інформації виникла помилка.', category='error')

            return redirect(url_for('main.devices'))
        else:
            flash('Інформацію про пристрій не оновлено, необхідні поля пусті.', category='warning')

    form = NewDeviceForm(device)

    return render_template('device.html', form=form, header="Редагування інформації про пристрій")


@main.route('/devices', methods=['GET'])
@login_required
def devices():
    devices = Device.query.all()

    if len(devices) == 0:
        return render_template('devices.html',
                               table='<p class="subtitle is-italic has-text-dark has-text-centered" '
                                     'style="padding:20px;">'
                                     'Зареєстрованих пристроїв не знайдено</p>')

    table = DeviceTable(devices)
    return render_template('devices.html', table=table)


@main.route('/computers/add', methods=['GET', 'POST'])
@login_required
def add_computer():
    form = NewComputerForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            created_computer = Computer(mac=form.mac.data.upper(), number=form.number.data,
                                        room=form.room.data)

            created_computer.is_blocked = 0

            db.session.add(created_computer)
            try:
                db.session.commit()
                flash('Комп`ютер успішно додано.', category='success')
                return redirect(url_for('main.dashboard'))
            except IntegrityError:
                db.session.rollback()
                flash('Комп`ютер вже існує.', category='error')

            return redirect(url_for('main.dashboard'))
        else:
            flash('Комп`ютер не додано, необхідні поля пусті.', category='warning')

    return render_template('computer.html', form=form, header="Новий комп'ютер")


@main.route('/computers/<computer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_computer(computer_id):
    computer = Computer.query.filter_by(id=computer_id).first_or_404()

    if request.method == 'POST':
        form = NewComputerForm()
        if form.validate_on_submit():
            computer.mac = form.mac.data
            computer.number = form.number.data
            computer.room = form.room.data
            db.session.merge(computer)
            try:
                db.session.commit()
                flash('Інформацію про комп`ютер успішно оновлено.', category='success')
                return redirect(url_for('main.computers'))
            except IntegrityError:
                db.session.rollback()
                flash('При оновленні інформації виникла помилка.', category='error')

            return redirect(url_for('main.computers'))
        else:
            flash('Інформацію про комп`ютер не оновлено, необхідні поля пусті.', category='warning')

    form = NewComputerForm(computer)

    return render_template('computer.html', form=form, header="Редагування інформації про комп`ютер")


@main.route('/computers', methods=['GET'])
@login_required
def computers():
    computers = Computer.query.order_by(Computer.room).all()

    if len(computers) == 0:
        return render_template('computers.html',
                               table='<p class="subtitle is-italic has-text-dark has-text-centered" '
                                     'style="padding:20px;">'
                                     'Компʼютерів не знайдено</p>')

    table = ComputerTable(computers)
    return render_template('computers.html', table=table)


if __name__ == '__main__':
    app = create_app()
    # with app.test_request_context():
    #     db.create_all()
    #     db.session.commit()

    app.run(debug=True)
