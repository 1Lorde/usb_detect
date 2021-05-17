from flask_table import Table, Col, DatetimeCol, DateCol

from models import Computer
from utils import check_drive


class ComputerMACCol(Col):
    def td_format(self, content):
        computer = Computer.query.filter_by(id=content).first()
        if not computer.mac:
            return 'Невідома'

        return computer.mac


class ComputerNumberCol(Col):
    def td_format(self, content):
        computer = Computer.query.filter_by(id=content).first()
        if not computer.number:
            return "Невідомо"
        return computer.number


class ComputerRoomCol(Col):
    def td_format(self, content):
        computer = Computer.query.filter_by(id=content).first()
        if not computer.room:
            return "Невідомо"
        return computer.room


class DeviceAllowedCol(Col):
    def td_format(self, content):
        is_allowed = check_drive(content)
        if not is_allowed:
            return '<span class="tag is-medium is-rounded is-light is-danger">Ні</span>'

        return '<span class="tag is-medium is-rounded is-light is-success">Так</span>'


class EventTable(Table):
    classes = ['table', 'is-striped', 'is-hoverable', 'is-fullwidth']
    time = DatetimeCol('Час', datetime_format='HH:mm:ss')
    date = DateCol('Дата', date_format='dd.MM.yyyy')
    device_serial = Col('Серійний № пристрою')
    device_vendor_id = Col('Виробник')
    device_product_id = Col('Модель')
    device_allowed = DeviceAllowedCol('Зареєстрований пристрій')
    ip = Col("IP-адреса")
    computer_mac = ComputerMACCol('MAC-адреса')
    computer_room = ComputerRoomCol('Аудиторія')
    computer_number = ComputerNumberCol('№ комп`ютера')


class ComputerTable(Table):
    classes = ['table', 'is-striped', 'is-hoverable', 'is-fullwidth']
    id = Col("ID")
    mac = Col('MAC-адреса')
    room = Col('Аудиторія')
    number = Col('Номер машини')

    def get_tr_attrs(self, item):
        return {"onclick": 'window.location="/computers/' + str(item.id) + '/edit"'}


class DeviceTable(Table):
    classes = ['table', 'is-striped', 'is-hoverable', 'is-fullwidth']
    id = Col("ID")
    name = Col('Назва')
    serial = Col('Серійний номер')
    vendor_id = Col('Виробник')
    product_id = Col('Модель')

    def get_tr_attrs(self, item):
        return {"onclick": 'window.location="/devices/' + str(item.id) + '/edit"'}
