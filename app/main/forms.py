#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField,DateTimeField,DateField,FloatField,IntegerField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    # name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('我的介绍')
    submit = SubmitField('提交')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[ Required()])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class DeviceSolidForm(Form):
    acceptance_date = DateField("现场验收日期(格式2015-1-1)", validators=[Required()])
    name = StringField("名称", validators=[Required()])
    type = StringField("型号", validators=[Required()])
    solid_number = StringField("数量", validators=[Required()])
    user_department = StringField("使用分厂", validators=[Required()])
    user_team = StringField("使用班组", validators=[Required()])
    equipment_number = StringField("设备编号", validators=[Required()])
    location = StringField("地点", validators=[Required()])
    device_status = StringField("设备状态", validators=[Required()])
    remarks_solid = StringField("备注")

    device_solid_submit = SubmitField('增加设备信息')
    
