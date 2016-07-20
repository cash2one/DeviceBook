#encoding:utf-8
import sys,os,flask
reload(sys)
sys.setdefaultencoding('utf8')

from datetime import datetime
import hashlib
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    '''
    PURCHASE 添加申购单权限
    PURCHASE_DEV 添加申购单设备权限
    CONTRACT 添加合同权限
    CONTRACT_DEV 添加合同设备权限
    BIND_DEV 绑定合同权限
    PAY_PLAN 添加付款计划权限
    PAYMENT 付款情况
    INVOICE 发票权限
    SOLID 验收权限
    ADMINISTER 管理员权限
    '''
    PURCHASE = 0x001
    PURCHASE_DEV = 0x002
    CONTRACT = 0x004
    CONTRACT_DEV = 0x008
    BIND_DEV = 0x010
    PAY_PLAN = 0x020
    PAYMENT = 0x040
    INVOICE = 0x080
    SOLID = 0x0100
    ADMINISTER = 0x0800
    READ = 0x0200





class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.String(64), index=True,unique=True,nullable=False)   #此处定义了unique和索引
    budget = db.Column(db.Float)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    devices = db.relationship('Device', backref='purchase', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.purchase_id

# class Bind_List(db.Model):
#     __tablename__ = 'bind_lists'
#
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#
#     device_id = db.Column(db.Integer,db.ForeignKey('devices.id'),primary_key=True)
#     contract_device_number_id = db.Column(db.Integer,db.ForeignKey('contract_device_numbers.id'),primary_key=True)
 

class Device(db.Model):
    __tablename__ = 'devices'   #申购单设备表
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(64))
    team = db.Column(db.String(64))
    applicant = db.Column(db.String(12))
    device_name = db.Column(db.String(64))
    project_leader = db.Column(db.String(12))
    remarks_device = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    purchase_contract_device_number = db.relationship('Contract_Device_Number', backref='purchase_contract_device_number', uselist=False)
    # device = db.relationship('Bind_List',
    #     foreign_keys=[Bind_List.device_id],
    #     backref=db.backref('device', lazy='joined'),
    #     lazy='dynamic',
    #     cascade='all,delete-orphan')

        
    def __repr__(self):
        return '<device_name %r>' % self.device_name


class Contract(db.Model):
    __tablename__ = 'contracts'   #合同表
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(64),unique=True,nullable=False)
    material_operator = db.Column(db.String(64))
    contract_date = db.Column(db.DateTime, index=True)
    contract_value = db.Column(db.Float)
    planned_arrival_date = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    contract_device = db.relationship('Contract_Device', backref='contract_device', lazy='dynamic')

    def __repr__(self):
        return '<Contract_number %r>' % self.contract_number


class Contract_Device(db.Model):
    __tablename__ = 'contract_devices'    # 合同设备表
    id = db.Column(db.Integer, primary_key=True)
    contract_subject_matter = db.Column(db.String(64))
    model = db.Column(db.String(64))
    supplier = db.Column(db.String(64))
    unit_price = db.Column(db.Float)
    device_quantity = db.Column(db.Integer)
    settlement_amount = db.Column(db.Float)
    #effective_date = db.Column(db.DateTime, index=True)
    remarks_contract_device = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    payment_situation = db.relationship('Payment_Situation', backref='payment_situation' )
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    contract_device_number = db.relationship('Contract_Device_Number', backref='contract_device_number', lazy='dynamic')

    @property
    def paid_amount(self):
        return "paidAmount"
    @property
    def unpaid_amount(self):
        return "unpaidAmount"
    @property
    def remaining_percentage(self):
        return "remainingPercentage"
    def __repr__(self):
        return '<User %r>' % self.contract_subject_matter


class Contract_Device_Number(db.Model):
    __tablename__ = 'contract_device_numbers'    # 合同设备表
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.Integer)
    contract_device_id = db.Column(db.Integer, db.ForeignKey('contract_devices.id'))
    device_invoice = db.relationship('Device_Invoice', backref='device_invoice', uselist=False)
    device_solid = db.relationship('Device_Solid', backref='device_solid', lazy='dynamic')

    purchase_device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))

    # purchase_device = db.relationship('Bind_List',
    #     foreign_keys=[Bind_List.contract_device_number_id],
    #     backref=db.backref('purchase_device', lazy='joined'),
    #     lazy='dynamic',
    #     cascade='all,delete-orphan')\


    def __repr__(self):
        return '<User %r>' % self.serial_number

class Device_Invoice(db.Model):
    __tablename__ = 'device_invoices'    #设备发票表
    id = db.Column(db.Integer, primary_key=True)
    invoice_type = db.Column(db.String(64))
    invoice_number = db.Column(db.String(64))
    voucher_id = db.Column(db.String(64))
    account_subject = db.Column(db.String(64))
    price_excluding_Tax = db.Column(db.Float)
    price_including_Tax = db.Column(db.Float)
    fixed_asset_date = db.Column(db.DateTime, index=True)
    financial_number = db.Column(db.String(64))
    remarks_invoice = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    contract_device_number_id = db.Column(db.Integer, db.ForeignKey('contract_device_numbers.id'))

    def __repr__(self):
        return '<User %r>' % self.invoice_number


class Payment_Situation(db.Model):
    __tablename__ = 'payment_situations'   #设备付款情况表(物资部)
    id = db.Column(db.Integer, primary_key=True)
    payment_times = db.Column(db.Integer)
    payment_content = db.Column(db.Text)
    due_date = db.Column(db.DateTime, index=True)
    proportion = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #payment=db.relationship('Payment',backref='payment' )
    contract_device_id = db.Column(db.Integer, db.ForeignKey('contract_devices.id'))

    def __repr__(self):
        return '<payment %r,%r>' % self.payment_times,self.payment_content

class Payment(db.Model):
    __tablename__ = 'payments'   #设备付款表(财务部）
    id = db.Column(db.Integer, primary_key=True)
    payment_date = db.Column(db.DateTime, index=True)
    pay_voucher_id = db.Column(db.String(64))
    pay_account_subject = db.Column(db.String(64))
    payment_money = db.Column(db.Float)
    con = db.Column(db.String(8),default='@')
    payment_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    pay_payment_times = db.Column(db.Integer)#, db.ForeignKey('payment_situations.payment_times')
    contract_device_number_id = db.Column(db.Integer, db.ForeignKey('contract_device_numbers.id'))

    def __repr__(self):
        return '<payment %r>' % self.payment_tvoucher_id
    @property
    def payment_amount(self):
        return "paymentAmount"


class Device_Solid(db.Model):
    __tablename__ = 'device_solids'    #设备转固表
    id = db.Column(db.Integer, primary_key=True)
    acceptance_date = db.Column(db.DateTime, index=True)
    name = db.Column(db.String(64))
    type = db.Column(db.String(64))
    solid_number = db.Column(db.String(64))
    user_department = db.Column(db.String(64))
    user_team = db.Column(db.String(64))
    equipment_number = db.Column(db.String(64))
    location = db.Column(db.String(64))
    device_status = db.Column(db.String(64))
    remarks_solid = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    contract_device_number_id = db.Column(db.Integer, db.ForeignKey('contract_device_numbers.id'))

    def __repr__(self):
        return '<User %r>' % self.invoice_number


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():

        roles = {
                    'Reader':(Permission.READ ,True),
                    'Financial': (Permission.PAYMENT |
                         Permission.INVOICE,False ),
                    'Material': (Permission.CONTRACT |
                         Permission.CONTRACT_DEV |
                         Permission.BIND_DEV |
                         Permission.PAY_PLAN ,False) ,
                    'Device':(Permission.PURCHASE |
                         Permission.PURCHASE_DEV |
                         Permission.SOLID ,False),

                    'Administrator': (0xfff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    #email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(64))
    department = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))



    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.department == '管理员':
                self.role = Role.query.filter_by(permissions=0xfff).first()
            # if self.role is None:
            #     self.role = Role.query.filter_by(default=True).first()
        # if self.email is not None and self.avatar_hash is None:
        #     self.avatar_hash = hashlib.md5(
        #         self.email.encode('utf-8')).hexdigest()
        #self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        # hash = self.avatar_hash or hashlib.md5(
        #     self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)




