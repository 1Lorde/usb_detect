from models import Event
from server.models import Device


def check_drive(serial_number):
    allowed_drive = Device.query.filter_by(serial=serial_number).first()
    if allowed_drive:
        return True
    else:
        return False


def get_device_info(vid, pid):
    vid = vid.split('_')[1]
    pid = pid.split('_')[1]
    vendor, product = None, None

    with open('static/usb.ids.txt') as f:
        for line in f:
            if vid in line:
                vendor = line
            if vendor and line.startswith("\t"):
                if pid in line:
                    product = line
                    break

    if vendor:
        vendor = vendor.split('  ')[1]
        vendor = vendor.replace("\n", "")
    if product:
        product = product.split('  ')[1]
        product = product.replace("\n", "")

    return vendor, product


def get_stats():
    devices_from_events = Event.query.with_entities(Event.device_serial).all()
    registered_devices = Device.query.with_entities(Device.serial).all()

    counter = 0
    for dev in devices_from_events:
        if dev in registered_devices:
            counter += 1

    return {'total': len(devices_from_events),
            'registered': counter,
            'unauthorized': len(devices_from_events) - counter}
