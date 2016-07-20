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


class PostForm(Form):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')


class PurchaseForm(Form):
    purchase_id = StringField("申购单编号", validators=[Required()])
    budget = StringField("设备预算金额（元）", validators=[Required()])
    purchase_submit = SubmitField('新增申购单')

class DeviceForm(Form):
    department = StringField("部门", validators=[Required()])
    team = StringField("班组", validators=[Required()])
    applicant= StringField("申请人", validators=[Required()])
    device_name = StringField("设备名称", validators=[Required()])
    project_leader = StringField("项目负责人", validators=[Required()])

    remarks_device = StringField("备注")

    device_submit = SubmitField('新增设备')

class ContractForm(Form):
    contract_number = StringField("合同号    ", validators=[Required()])
    material_operator = StringField("物资部经办人", validators=[Required()])
    contract_date = DateField ("合同签订日期(格式2015-1-1)",validators=[Required()]) #format='%y-%m-%d'
    contract_value = FloatField("原合同总额", validators=[Required()])
    planned_arrival_date = DateField("合同计划日期(格式2015-1-1)", validators=[Required()])

    contract_submit = SubmitField('新增合同')

class BindDeviceForm(Form):
    id = SelectField("绑定申购单编号")
    contract_device_submit = SubmitField('绑定该设备到合同')

class ContractDeviceForm(Form):
    contract_subject_matter = StringField("合同标的物名称", validators=[Required()])
    model = StringField("型号", validators=[Required()])
    supplier = StringField("供应单位", validators=[Required()])
    unit_price= FloatField("原合同单价", validators=[Required()])
    device_quantity = IntegerField("数量", validators=[Required()])
    settlement_amount = StringField("结算金额", validators=[Required()])
    #effective_date = DateField("实际到货日期（不填，待删）")
    remarks_contract_device = StringField("备注")

    contract_subject_submit = SubmitField('新增设备')


class PaymentForm(Form):
    pay_payment_times = IntegerField("付款次数", validators=[Required()])
    payment_date = DateField("付款日期")
    pay_voucher_id = StringField("凭证号", validators=[Required()])
    pay_account_subject = StringField("入账科目（借）", validators=[Required()])
    payment_money = FloatField('金额', validators=[Required()])

    payment_submit = SubmitField('提交付款')


class DeviceInvoiceForm(Form):
    invoice_type = StringField("发票类型", validators=[Required()])
    invoice_number = StringField("发票号码", validators=[Required()])
    voucher_id = StringField("凭证号", validators=[Required()])
    account_subject = StringField("入账科目（借）", validators=[Required()])
    price_excluding_Tax = FloatField("发票金额（不含税）/元", validators=[Required()])
    price_including_Tax = FloatField("发票金额（含税）/元", validators=[Required()])
    fixed_asset_date = DateField("转固日期")
    financial_number = StringField("财务编号", validators=[Required()])
    remarks_invoice = StringField("备注")

    device_invoice_submit = SubmitField('增加合同信息')

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
    
    
    
class PaymentSituationForm(Form):
    payment_times = IntegerField("付款次数", validators=[Required()])
    payment_content = StringField("付款内容", validators=[Required()])
    due_date = DateField("应付日期")
    proportion = FloatField("比例", validators=[Required()])

    payment_submit = SubmitField('提交付款')
