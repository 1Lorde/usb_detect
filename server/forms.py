from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class NewDeviceForm(FlaskForm):
    name = StringField("Назва")
    serial = StringField("Серійний номер", validators=[DataRequired()])
    submit = SubmitField("Зберегти")

    def __init__(self, device=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if device:
            self.name.data = device.name
            self.serial.data = device.serial


class NewComputerForm(FlaskForm):
    mac = StringField("MAC", validators=[DataRequired(), Regexp(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$')])
    number = StringField("Номер", validators=[DataRequired()])
    room = StringField("Аудиторія", validators=[DataRequired()])
    submit = SubmitField("Зберегти")

    def __init__(self, computer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if computer:
            self.mac.data = computer.mac
            self.number.data = computer.number
            self.room.data = computer.room
