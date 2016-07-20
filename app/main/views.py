#encoding:utf-8
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
from sqlalchemy import Column, null,func,and_,desc
import json,flask
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm,PurchaseForm,DeviceForm,ContractForm,ContractDeviceForm,\
    BindDeviceForm,PaymentForm,DeviceInvoiceForm,DeviceSolidForm,PaymentSituationForm
from .. import db
from ..models import Permission, Role, User, Purchase, Device, Contract, Device_Invoice, Contract_Device,\
    Payment,Payment_Situation,Device_Solid,Contract_Device_Number
from ..decorators import admin_required, permission_required

def replace_none(sql_result):
    '''
    替换sql结果中的none
    :param sql_result:
    :return:
    '''
    result=[]
    for first in sql_result:
        tmp=[]
        for second in first:
            if second is None:
                second=''
            tmp.append(second)
        result.append(tmp)
    return result


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #page = request.args.get('page', 1, type=int)
    #pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        # page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        # error_out=False)
    #posts = pagination.items
    return render_template('user.html', user=user) #posts=posts,
    #                        pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        #current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    #form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)



@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
#@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
#@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
#@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
#@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
#@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/about')

def about():
    explain= [['前端框架','Bootstrap'],['服务器','Apache+mod_wsgi'],['图形库','Echarts'],['后端框架','python2.7+Flask'],
              ['数据库','SQLite3'],['ORM','flask-sqlalchemy'],['','']]
    return render_template('about.html',explain=explain)


@main.route('/insert_purchase', methods=['GET', 'POST'])
#@login_required
def insert_purchase():
    form = PurchaseForm()

    if  form.validate_on_submit() and current_user.can(Permission.PURCHASE):
        purchase = Purchase(purchase_id=form.purchase_id.data,budget=form.budget.data)
        if not Purchase.query.filter_by(purchase_id=form.purchase_id.data).first():
            db.session.add(purchase)
            db.session.commit()
        else:
            db.session.rollback()
            flash("您可能输入了重复的请购单号或者非法字符，请重新刷新网页")
        return redirect(url_for('.insert_purchase'))
    elif form.validate_on_submit() and not current_user.can(Permission.PURCHASE) :
        flash("你没有权限写入申购单")
        return redirect(url_for('.insert_purchase'))

    page = request.args.get('page', 1, type=int)
    pagination = Purchase.query.order_by(Purchase.timestamp.desc()).outerjoin(Device).add_entity(Device).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    purchases = pagination.items
    return render_template('insert_purchase.html', form=form, purchases=purchases,pagination=pagination)

#bind_id是合同设备里每个设备的id号，choice是申购单中设备的id号
@main.route('/bind_device/<int:bind_id>', methods=['GET', 'POST'])
#@login_required
def bind_device(bind_id):
    form = BindDeviceForm()

    purchases = Device.query.outerjoin(Purchase).add_entity(Purchase).all() #找出所有申购单
    if not purchases:
        flash('没有申购单设备，无法绑定')
        return redirect(url_for('.insert_contract'))
    form.id.choices = [(v.Device.id,str(v.Purchase.purchase_id)+"        "+v.Device.device_name) for k,v in enumerate(purchases)]  #写入下拉列表内容
    choice=str(form.id.data)   #得到用户选择的选项

    if  choice!='None' and current_user.can(Permission.BIND_DEV):
        
        choice = int(choice)
        db.session.query(Contract_Device_Number).filter(Contract_Device_Number.id==bind_id).update({Contract_Device_Number.purchase_device_id:choice})
        db.session.commit()
        return redirect(url_for('.insert_contract'))

    elif choice!='None' and not current_user.can(Permission.BIND_DEV):
        flash("你没有权限绑定设备")
        return redirect(url_for('.insert_contract'))
    return render_template('bind_device.html', form=form)

@main.route('/insert_device/<int:id>', methods=['GET', 'POST'])
#@login_required
def insert_device(id):
    form = DeviceForm()
    purchase = Purchase.query.filter_by(id=id).first()
    if  form.validate_on_submit() and current_user.can(Permission.PURCHASE_DEV):
        device = Device(department=form.department.data,team=form.team.data,\
            applicant=form.applicant.data,device_name=form.device_name.data,\
            project_leader=form.project_leader.data,\
            remarks_device=form.remarks_device.data,purchase=purchase)    #将表单信息插入devices表
        db.session.add(device)
        db.session.commit()
        flash("添加设备成功，你可以继续添加该申购单下的设备信息")
        return redirect(url_for('.insert_device',id=id))
    elif form.validate_on_submit() and not current_user.can(Permission.PURCHASE_DEV):
        flash("你没有权限写入设备")
        return redirect(url_for('.insert_device',id=id))
    devices = Device.query.filter_by(purchase_id=purchase.id).order_by(Device.timestamp.desc()).all() #.filter_by(XXX)
    return render_template('insert_device.html', form=form, devices=devices,purchase=purchase)


@main.route('/insert_contract', methods=['GET', 'POST'])
#@login_required
def insert_contract():
    form = ContractForm()
    page = request.args.get('page', 1, type=int)
    pagination = Contract.query.order_by(desc(Contract.timestamp)).outerjoin(Contract_Device).add_entity(Contract_Device).outerjoin(Contract_Device_Number)\
        .add_entity(Contract_Device_Number).outerjoin(Device).add_entity(Device).outerjoin(Purchase).add_entity(Purchase)\
        .paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    contracts = pagination.items

    if  form.validate_on_submit() and current_user.can(Permission.CONTRACT):
        contract = Contract(contract_number=form.contract_number.data,material_operator=form.material_operator.data,\
            contract_date=form.contract_date.data,contract_value=form.contract_value.data,\
            planned_arrival_date=form.planned_arrival_date.data)

        if  not Contract.query.filter_by(contract_number=form.contract_number.data).first():
            db.session.add(contract)
            db.session.commit()
        else:
            db.session.rollback()
            flash("您可能输入了重复的合同编号或者非法字符，请重新刷新网页")
        return redirect(url_for('.insert_contract'))

    elif form.validate_on_submit() and not current_user.can(Permission.PURCHASE) :
        flash('你没有权限写入合同')
        return redirect(url_for('.insert_contract'))

    return render_template('insert_contract.html', form=form, contracts=contracts,pagination=pagination)




@main.route('/insert_contract_device/<int:id>', methods=['GET', 'POST'])
#@login_required
def insert_contract_device(id):
    form = ContractDeviceForm()
    contract = Contract.query.filter_by(id=id).first()   #已经添加的合同设备
    if  form.validate_on_submit() and current_user.can(Permission.CONTRACT_DEV):
        device_quantity=int(form.device_quantity.data)
        if device_quantity!=form.device_quantity.data:
            flash('设备数量必须为整数')
            return redirect(url_for('.insert_contract_subject',id=id))
        contract_device = Contract_Device(contract_subject_matter=form.contract_subject_matter.data,model=form.model.data,supplier=form.supplier.data,\
            unit_price=form.unit_price.data,device_quantity=form.device_quantity.data,\
            settlement_amount=form.settlement_amount.data,\
            remarks_contract_device=form.remarks_contract_device.data,\
            contract_device=contract)    #将表单信息插入devices表
        db.session.add(contract_device)
        db.session.commit()

        #功能为提交一次合同设备内容，则根据设备数量n提交n个合同设备细项
        for i in range(device_quantity):
            contract_device_number=Contract_Device_Number(serial_number=i+1, contract_device_number=contract_device)
            db.session.add(contract_device_number)
            db.session.commit()
        return redirect(url_for('.insert_contract_device',id=id))
    elif form.validate_on_submit() and not current_user.can(Permission.CONTRACT_DEV) :
        flash('你没有权限写入合同设备')
        return redirect(url_for('.insert_contract_device',id=id))

    contract_devices = Contract_Device.query.filter_by(contract_id=id).order_by(Contract_Device.timestamp.desc()).all() #.filter_by(XXX)
    return render_template('insert_contract_device.html', form=form, contract=contract,contract_devices=contract_devices)


@main.route('/insert_payment_situation/<int:id>', methods=['GET', 'POST'])
#@login_required
def insert_payment_situation(id):
    form = PaymentSituationForm()
    contract_device = Contract_Device.query.filter_by(id=id).first()
    payment_situations = Payment_Situation.query.filter_by(contract_device_id=id).all()

    if  form.validate_on_submit() and current_user.can(Permission.PAY_PLAN):
        payment_situation = Payment_Situation.query.filter_by(contract_device_id=id).filter_by(payment_times=form.payment_times.data).first()
        if payment_situation:
             db.session.delete(payment_situation)

        payment_situation = Payment_Situation(payment_times=form.payment_times.data,payment_content=form.payment_content.data,\
            due_date=form.due_date.data,proportion=form.proportion.data,payment_situation=contract_device)    #将表单信息插入devices表
        db.session.add(payment_situation)
        db.session.commit()
        return redirect(url_for('.insert_payment_situation',id=id))
    elif form.validate_on_submit() and not current_user.can(Permission.PAY_PLAN) :
        flash('你没有权限写入')
        return redirect(url_for('.insert_payment_situation',id=id))

    return render_template('insert_payment_situation.html', form=form, payment_situations=payment_situations,contract_device=contract_device)


@main.route('/insert_payment/<int:id>', methods=['GET', 'POST'])
#@login_required
def insert_payment(id):
    form = PaymentForm()
    #此处特别注意payment 和payment_situation并没有外键联系，故需要加入双条件Join，and_(Payment_Situation.payment_times==Payment.pay_payment_times ,Payment.contract_device_number_id==id) 以防止重复
    contract_device_id = Contract_Device_Number.query.filter_by(id=id).first().contract_device_id
    payment = Payment_Situation.query.filter_by(contract_device_id=contract_device_id).outerjoin(Contract_Device).add_entity(Contract_Device).\
        outerjoin(Payment,and_(Payment_Situation.payment_times==Payment.pay_payment_times ,Payment.contract_device_number_id==id)).add_entity(Payment)

    if  form.validate_on_submit() and current_user.can(Permission.PAYMENT):
        payment = Payment.query.filter_by(contract_device_number_id=id).filter_by(pay_payment_times=form.pay_payment_times.data).first()
        if payment:
             db.session.delete(payment)
        payment = Payment(payment_date=form.payment_date.data,pay_voucher_id=form.pay_voucher_id.data,\
            pay_account_subject=form.pay_account_subject.data,payment_money=form.payment_money.data,\
            contract_device_number_id=id,pay_payment_times=form.pay_payment_times.data)
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('.insert_payment',id=id))
    elif form.validate_on_submit() and not current_user.can(Permission.PURCHASE) :
        flash('你没有权限写入')
        return redirect(url_for('.insert_payment',id=id))
    return render_template('insert_payment.html', form=form,payment=payment)


@main.route('/insert_device_invoice/<int:id>', methods=['GET', 'POST'])
#@login_required
def insert_device_invoice(id):
    form = DeviceInvoiceForm()
    contract_device_number = Contract_Device_Number.query.filter_by(id=id).first()

    if  form.validate_on_submit() and current_user.can(Permission.INVOICE):
        device_invoice = Device_Invoice.query.filter_by(contract_device_number_id=id).first()
        if device_invoice:
             db.session.delete(device_invoice)
        device_invoice = Device_Invoice(invoice_type=form.invoice_type.data, invoice_number=form. invoice_number.data,\
            voucher_id=form.voucher_id.data,\
            account_subject=form.account_subject.data,price_excluding_Tax=form.price_excluding_Tax.data,\
            price_including_Tax=form.price_including_Tax.data,fixed_asset_date=form.fixed_asset_date.data,\
            financial_number=form.financial_number.data, remarks_invoice=form. remarks_invoice.data,\
            device_invoice=contract_device_number)
        db.session.add(device_invoice)
        db.session.commit()
        return redirect(url_for('.insert_device_invoice',id=id))
    elif form.validate_on_submit() and not current_user.can(Permission.PURCHASE) :
        flash('你没有权限写入')
        return redirect(url_for('.insert_device_invoice',id=id))
    device_invoices =Device_Invoice.query.filter_by(contract_device_number_id=id).all()
    return render_template('insert_device_invoice.html', form=form,device_invoices=device_invoices,contract_device_number=contract_device_number)


@main.route('/insert_device_solid/<int:id>', methods=['GET', 'POST'])
#@login_required
def insert_device_solid(id):
    form = DeviceSolidForm()
    device_solids =Device_Solid.query.filter_by(contract_device_number_id=id).all()

    if form.validate_on_submit() and current_user.can(Permission.SOLID) :
        device_solid = Device_Solid.query.filter_by(contract_device_number_id=id).first()
        if device_solid:
             db.session.delete(device_solid)
        device_solid = Device_Solid(acceptance_date=form.acceptance_date.data,name=form.name.data,\
            type=form.type.data,solid_number=form.solid_number.data,user_department=form.user_department.data,\
            user_team=form.user_team.data,equipment_number=form.equipment_number.data,\
            location=form.location.data, device_status=form.device_status.data,remarks_solid=form.remarks_solid.data,
            contract_device_number_id =id)
        db.session.add(device_solid)
        db.session.commit()
        return redirect(url_for('.insert_device_solid',id=id))
    elif form.validate_on_submit() and not current_user.can(Permission.SOLID) :
        flash('你没有权限写入')
        return redirect(url_for('.insert_device_solid',id=id))
    return render_template('insert_device_solid.html', form=form,device_solids=device_solids)


@main.route('/all', methods=['GET', 'POST'])
#@login_required
def all():


# 用ORM写的如下
#     # purchase = Contract_Device_Number.query.outerjoin(Contract_Device).add_entity(Contract_Device)\
#     #     .outerjoin(Device).add_entity(Device).outerjoin(Purchase).add_entity(Purchase)\
#     #     .outerjoin(Payment_Situation,Payment_Situation.contract_device_id==Contract_Device.id).add_entity(Payment_Situation)\
#     #     .outerjoin(Payment,and_(Payment_Situation.payment_times==Payment.pay_payment_times,Payment.contract_device_number_id == Contract_Device_Number.id)).add_entity(Payment)\
#     #     .outerjoin(Contract).add_entity(Contract).outerjoin(Device_Invoice).add_entity(Device_Invoice)\
#     #     .outerjoin(Device_Solid).add_entity(Device_Solid).all()
#     # return render_template('all-2.html',purchase=purchase)
#
# 用原生sql写,下面是所有的内容

    # results = db.session.execute('select * from contract_device_numbers \
    #         left join device_invoices on device_invoices.contract_device_number_id=contract_device_numbers.id\
    #         left join device_solids on device_solids.contract_device_number_id=contract_device_numbers.id\
    #         left join contract_devices on contract_devices.id=contract_device_numbers.contract_device_id\
    #         left join contracts on contracts.id= contract_devices.contract_id \
    #         left join payment_situations on payment_situations.contract_device_id=contract_devices.id\
    #         left join payments on contract_device_numbers.id=payments.contract_device_number_id and payment_situations.payment_times=payments.pay_payment_times\
    #         left join devices on devices.id=contract_device_numbers.purchase_device_id                     \
    #         left join purchases on purchases.id=devices.purchase_id')

    results = db.session.execute('select * ,max(第一次付款) PPP_1,max(第二次付款) PPP_2 ,max(第三次付款) PPP_3,max(第四次付款) PPP_4,max(第五次付款) PPP_5,max(第六次付款) PPP_6        \
            from ( select *,\
                case payments.pay_payment_times when 1 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第一次付款,\
                case payments.pay_payment_times when 2 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第二次付款 , \
                case payments.pay_payment_times when 3 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第三次付款,\
                case payments.pay_payment_times when 4 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第四次付款 ,\
                case payments.pay_payment_times when 5 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第五次付款 , \
                case payments.pay_payment_times when 6 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第六次付款\
                 from contract_device_numbers \
            left join device_invoices on device_invoices.contract_device_number_id=contract_device_numbers.id\
            left join device_solids on device_solids.contract_device_number_id=contract_device_numbers.id\
            left join contract_devices on contract_devices.id=contract_device_numbers.contract_device_id\
            left join contracts on contracts.id= contract_devices.contract_id \
            left join payment_situations on payment_situations.contract_device_id=contract_devices.id\
            left join payments on contract_device_numbers.id=payments.contract_device_number_id and payment_situations.payment_times=payments.pay_payment_times\
            left join devices on devices.id=contract_device_numbers.purchase_device_id                     \
            left join purchases on purchases.id=devices.purchase_id) as t group by t.id \
            ').fetchall()

    # def split_alpha(results):
    #     res=[]
    #     return str(results)
    #     for data in results:
    #         tmp={}
    #
    #         for (k,v) in data.items():
    #             if k[0:4]=='ppp_':
    #                 tmp[k]=v.split('@')
    #             else:
    #                 tmp[k]=v
    #         res.append(tmp)
    #     return res
    # results=split_alpha(results)
    # return str(results[0])
    # return str(dict(c))

    # # results[0]['purchase_id']='gfhg'
    return render_template('all.html',results=results)


@main.route('/report', methods=['GET', 'POST'])
#@login_required
def report():

    #特别注意此处有distinct
    results = db.session.execute('select contracts.id,contracts.contract_number,contracts.material_operator,contract_value,sum(payments.payment_money),\
            round(((contract_value-sum(payments.payment_money))/contract_value),2),\
            count(distinct contract_device_numbers.id),count(distinct  device_invoices.id),\
            count(distinct device_solids.id) from contract_device_numbers \
            left join device_invoices on device_invoices.contract_device_number_id=contract_device_numbers.id\
            left join device_solids on device_solids.contract_device_number_id=contract_device_numbers.id\
            left join contract_devices on contract_devices.id=contract_device_numbers.contract_device_id\
            left join contracts on contracts.id= contract_devices.contract_id \
            left join payments on contract_device_numbers.id=payments.contract_device_number_id\
            group by contracts.contract_number\
            ').fetchall()

    #
    results=replace_none(results)

    return render_template('report.html',results=results)

@main.route('/contract_detail/<int:con_id>', methods=['GET', 'POST'])
#@login_required
def contract_detail(con_id):
    results = db.session.execute("select * ,max(第一次付款) PPP_1,max(第二次付款) PPP_2 ,max(第三次付款) PPP_3,max(第四次付款) PPP_4,max(第五次付款) PPP_5,max(第六次付款) PPP_6        \
            from ( select *,\
                case payments.pay_payment_times when 1 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第一次付款,\
                case payments.pay_payment_times when 2 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第二次付款 , \
                case payments.pay_payment_times when 3 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第三次付款,\
                case payments.pay_payment_times when 4 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第四次付款 ,\
                case payments.pay_payment_times when 5 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第五次付款 , \
                case payments.pay_payment_times when 6 then payments.pay_payment_times||con||payment_situations.payment_content||con||payment_situations.due_date||con||payments.payment_date||con||payments.pay_voucher_id||con||payments.pay_account_subject||con||payment_situations.proportion||con||payments.payment_money end as 第六次付款\
                 from contract_device_numbers \
            left join device_invoices on device_invoices.contract_device_number_id=contract_device_numbers.id\
            left join device_solids on device_solids.contract_device_number_id=contract_device_numbers.id\
            left join contract_devices on contract_devices.id=contract_device_numbers.contract_device_id\
            left join contracts on contracts.id= contract_devices.contract_id \
            left join payment_situations on payment_situations.contract_device_id=contract_devices.id\
            left join payments on contract_device_numbers.id=payments.contract_device_number_id and payment_situations.payment_times=payments.pay_payment_times\
            left join devices on devices.id=contract_device_numbers.purchase_device_id                     \
            left join purchases on purchases.id=devices.purchase_id where contracts.id=:id) as t group by t.id",{"id":con_id}).fetchall()

    return render_template('contract_detail.html',results=results)

@main.route('/diagram', methods=['GET', 'POST'])
#login_required
def diagram():
    return render_template('diagram.html')


@main.route('/data', methods=['GET', 'POST'])
#login_required
def data():
    purchases = db.session.execute('select department,count(department) from devices left join purchases on purchases.id=devices.purchase_id group by department').fetchall()

    p=[k[0] for k in purchases]
    q=[k[1] for k in purchases]

    data_json={'name':p,'value':q}

    return flask.jsonify(data_json)

@main.route('/export_pay_plan', methods=['GET', 'POST'])
#@login_required
def export_pay_plan():
    return render_template('export_pay_plan.html')

@main.route('/test')
def test():
    return render_template('test.html')




