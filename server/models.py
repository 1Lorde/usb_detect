from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import column_property, synonym

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(17), unique=True)
    number = db.Column(db.String(10))
    room = db.Column(db.String(10))

    def __repr__(self):
        return f'{self.room if None else "[XXX"}-{self.number if None else "X]"} (mac: {self.mac})'


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(100))
    vendor_id = db.Column(db.String(10))
    product_id = db.Column(db.String(20))
    name = db.Column(db.String(100))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_serial = db.Column(db.String(100))
    device_vendor_id = db.Column(db.String(10))
    device_product_id = db.Column(db.String(20))
    ip = db.Column(db.String(12))
    created_at = db.Column(db.DateTime())

    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False)
    computer = db.relationship('Computer', backref=db.backref('event', lazy=True))

    date = synonym('created_at')
    time = synonym('created_at')
    computer_mac = synonym('computer_id')
    computer_room = synonym('computer_id')
    computer_number = synonym('computer_id')
    device_allowed = synonym('device_serial')
