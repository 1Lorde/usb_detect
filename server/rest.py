import hashlib
from datetime import datetime

from flask import Blueprint, make_response, request

from utils import get_device_info
from . import db
from .models import Event, Computer, Device
from .utils import check_drive

rest = Blueprint('rest', __name__)


@rest.route("/devices/check", methods=['POST'])
def check():
    data = request.get_json()
    vendor, product = get_device_info(data['vendor_id'], data['product_id'])

    new_event = Event(device_serial=data['serial_number'],
                      device_vendor_id=vendor,
                      device_product_id=product,
                      ip=data['ip'],
                      created_at=datetime.now())

    if not Computer.query.filter_by(mac=data['mac']).first():
        computer = Computer(mac=data['mac'])
        db.session.add(computer)
        db.session.commit()

    computer_id = Computer.query.filter_by(mac=data['mac']).first().id

    new_event.computer_id = computer_id

    db.session.add(new_event)
    db.session.commit()

    if check_drive(data['serial_number']):
        dev = Device.query.filter_by(serial=data['serial_number']).first()
        if dev and (not dev.vendor_id or not dev.product_id):
            dev.vendor_id, dev.product_id = vendor, product
            db.session.merge(dev)
            db.session.commit()

        response = make_response("True", 200)
        response.mimetype = "text/plain"
        return response
    else:
        response = make_response("False", 200)
        response.mimetype = "text/plain"
        return response


@rest.route("/devices/allowed", methods=['GET'])
def allowed_devices():
    allowed_devs = Device.query.all()

    hashed_allowed = ''

    for dev in allowed_devs:
        h = hashlib.sha256()
        h.update(dev.serial.encode('utf-8'))
        hashed_allowed = hashed_allowed + h.hexdigest() + '\n'

    hashed_allowed = hashed_allowed[:-1]
    response = make_response(hashed_allowed, 200)
    response.mimetype = "text/plain"
    return response


@rest.route("/devices/allowed/hash", methods=['GET'])
def allowed_devices_hash():
    allowed_devs = Device.query.all()

    hashed_allowed = ''
    h = hashlib.sha256()

    for dev in allowed_devs:
        h.update(dev.serial.encode('utf-8'))
        hashed_allowed = hashed_allowed + h.hexdigest() + '\n'

    hashed_allowed = hashed_allowed[:-1]
    print(hashed_allowed)

    h = hashlib.sha256()
    h.update(hashed_allowed.encode('utf-8'))
    response = make_response(h.hexdigest(), 200)
    response.mimetype = "text/plain"
    return response