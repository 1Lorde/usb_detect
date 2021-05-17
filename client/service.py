import logging
import os
import socket
import time
from concurrent.futures.thread import ThreadPoolExecutor
from hashlib import sha256

import pythoncom
import requests
import wmi
from getmac import get_mac_address

from client.utils import load_config_file, add_exception_to_win_defender, add_to_registry

config = load_config_file()
SERVER_IP = config['server']['ip']
SERVER_PORT = config['server']['port']
DIR_PATH = config['dir_path']
LOCKER_FILENAME = config['locker_filename']
LOCAL_DB_FILENAME = config['local_db__filename']
LOG_FORMAT = config['logging']['format']
DATE_FORMAT = config['logging']['date_format']
UPDATE_TIMEOUT = config['update_timeout']

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

check_url = "http://{}:{}/check".format(SERVER_IP, SERVER_PORT)
allowed_url = "http://{}:{}/allowed".format(SERVER_IP, SERVER_PORT)
allowed_hash_url = "http://{}:{}/allowed/hash".format(SERVER_IP, SERVER_PORT)


def create_request_json(drive):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    return {"serial_number": drive["serial_number"],
            "mac": get_mac_address().upper(),
            "ip": local_ip,
            "account": os.getlogin()}


def is_allowed_latest():
    try:
        if not os.path.exists(LOCAL_DB_FILENAME):
            return False

        response = requests.get(allowed_hash_url).text
        h = sha256()
        with open(LOCAL_DB_FILENAME, 'r') as f:
            hashes = f.readline()

        h.update(hashes.encode('utf-8'))

        if response == h.hexdigest():
            logging.info('Local database of allowed devices are latest')
            return True
        else:
            logging.info('Local database of allowed devices are outdated')
            return False

    except Exception as e:
        logging.warning('Can`t get hash of allowed devices database, cause ' + str(type(e).__name__))


def update_allowed_drives():
    while True:
        if not is_allowed_latest():
            try:
                response = requests.get(allowed_url).text
                with open(LOCAL_DB_FILENAME, 'w') as f:
                    f.writelines(response)
                    logging.info('List of allowed devices successfully updated')
            except Exception as e:
                logging.warning('List of allowed devices not updated, cause ' + str(type(e).__name__))

        time.sleep(UPDATE_TIMEOUT)


def run_locker():
    try:
        # registry_path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        # key_my = OpenKey(HKEY_LOCAL_MACHINE, registry_path, 0, KEY_ALL_ACCESS)
        # SetValueEx(key_my, 'Lock', 0, REG_SZ, 'C:\\Program Files\\Windows Security\\SecureDrives\\usbl.exe')
        # CloseKey(key_my)
        #
        # os.startfile('C:\\Program Files\\Windows Security\\SecureDrives\\usbl.exe')
        #
        # user = "Virtual"
        # pword = "1111"
        # domain = "."  # means current domain
        # logontype = win32con.LOGON32_LOGON_INTERACTIVE
        # provider = win32con.LOGON32_PROVIDER_WINNT50
        # token = win32security.LogonUser(user, domain, pword, logontype, provider)
        #
        # # Now let's create the STARTUPINFO structure. Read the link above for more info on what these can do.
        # startup = win32process.STARTUPINFO()
        #
        # # Finally, create a cmd.exe process using the "ltorvalds" token.
        # appname = "C:\\Program Files\\Windows Security\\SecureDrives\\usbl.exe"
        # priority = win32con.NORMAL_PRIORITY_CLASS
        # win32process.CreateProcessAsUser(token, appname, None, None, None, True, priority, None, None, startup)
        if not os.path.exists('.lock'):
            open('.lock', 'x')
    except Exception as e:
        logging.warning('Can`t find locker program, cause ' + str(type(e).__name__))


def online_check(drive):
    response = requests.post(check_url, json=create_request_json(drive))
    if response.text == "False":
        logging.info('Drive {} not allowed'.format(drive['serial_number']))
        run_locker()

        # registry_path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        # key_my = OpenKey(HKEY_LOCAL_MACHINE, registry_path, 0, KEY_ALL_ACCESS)
        # DeleteValue(key_my, 'Lock')
        # CloseKey(key_my)
    else:
        logging.info('Drive allowed')


def offline_check(drive):
    if not os.path.exists(LOCAL_DB_FILENAME):
        logging.info('Local database is empty. Drive {} are blocked'.format(drive['serial_number']))
        run_locker()
        return

    h = sha256()
    h.update(drive['serial_number'].encode('utf-8'))
    if not h.hexdigest() in list(map(str.strip, open(LOCAL_DB_FILENAME, 'r'))):
        logging.info('Drive {} not allowed'.format(drive['serial_number']))
        run_locker()

        # registry_path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        # key_my = OpenKey(HKEY_LOCAL_MACHINE, registry_path, 0, KEY_ALL_ACCESS)
        # DeleteValue(key_my, 'Lock')
        # CloseKey(key_my)
    else:
        logging.info('Drive allowed')


def watch_drives():
    pythoncom.CoInitialize()

    # raw_wql = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBHub'"
    c = wmi.WMI()
    watcher = c.watch_for(notification_type='Creation', wmi_class='Win32_USBHub', delay_secs=2)

    while True:
        usb = watcher()
        id_property = usb.wmi_property("DeviceId").value
        drive = {
            "vendor_id": id_property.split("\\")[1].split("&")[0],
            "product_id": id_property.split("\\")[1].split("&")[1],
            "serial_number": id_property.split("\\")[2]
        }
        logging.info('Inserted drive: ' + str(create_request_json(drive)))

        try:
            online_check(drive)
        except Exception as e:
            logging.warning('Can`t send request, performing OFFLINE check, cause ' + str(e))
            offline_check(drive)


if __name__ == '__main__':
    # add_exception_to_win_defender(dir_path)
    # add_to_registry(dir_path, locker_filename)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(update_allowed_drives)
        logging.info("Task 'Auto updating' started")

        future2 = executor.submit(watch_drives)
        logging.info("Task 'Watching drives' started")
