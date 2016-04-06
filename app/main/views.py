#encoding:utf-8
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
from sqlalchemy import Column, null,func,and_,desc
import json,flask
import sqlite3
import os
import time,datetime
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Permission, Role, User,U8
from ..decorators import admin_required, permission_required


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


# @main.route('/follow/<username>')
# @login_required
# #@permission_required(Permission.FOLLOW)
# def follow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('Invalid user.')
#         return redirect(url_for('.index'))
#     if current_user.is_following(user):
#         flash('You are already following this user.')
#         return redirect(url_for('.user', username=username))
#     current_user.follow(user)
#     flash('You are now following %s.' % username)
#     return redirect(url_for('.user', username=username))


# @main.route('/unfollow/<username>')
# @login_required
# #@permission_required(Permission.FOLLOW)
# def unfollow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('Invalid user.')
#         return redirect(url_for('.index'))
#     if not current_user.is_following(user):
#         flash('You are not following this user.')
#         return redirect(url_for('.user', username=username))
#     current_user.unfollow(user)
#     flash('You are not following %s anymore.' % username)
#     return redirect(url_for('.user', username=username))
#
#
# @main.route('/followers/<username>')
# def followers(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('Invalid user.')
#         return redirect(url_for('.index'))
#     page = request.args.get('page', 1, type=int)
#     pagination = user.followers.paginate(
#         page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
#         error_out=False)
#     follows = [{'user': item.follower, 'timestamp': item.timestamp}
#                for item in pagination.items]
#     return render_template('followers.html', user=user, title="Followers of",
#                            endpoint='.followers', pagination=pagination,
#                            follows=follows)
#
#
# @main.route('/followed-by/<username>')
# def followed_by(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('Invalid user.')
#         return redirect(url_for('.index'))
#     page = request.args.get('page', 1, type=int)
#     pagination = user.followed.paginate(
#         page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
#         error_out=False)
#     follows = [{'user': item.followed, 'timestamp': item.timestamp}
#                for item in pagination.items]
#     return render_template('followers.html', user=user, title="Followed by",
#                            endpoint='.followed_by', pagination=pagination,
#                            follows=follows)
#
#
# @main.route('/followed')
# @login_required
# def show_followed():
#     resp = make_response(redirect(url_for('.index')))
#     resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
#     return resp
#
#
# @main.route('/moderate')
# @login_required
# #@permission_required(Permission.MODERATE_COMMENTS)
# def moderate():
#     page = request.args.get('page', 1, type=int)
#     pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
#         page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
#         error_out=False)
#     comments = pagination.items
#     return render_template('moderate.html', comments=comments,
#                            pagination=pagination, page=page)
#
#
# @main.route('/moderate/enable/<int:id>')
# @login_required
# #@permission_required(Permission.MODERATE_COMMENTS)
# def moderate_enable(id):
#     comment = Comment.query.get_or_404(id)
#     comment.disabled = False
#     db.session.add(comment)
#     return redirect(url_for('.moderate',
#                             page=request.args.get('page', 1, type=int)))
#
#
# @main.route('/moderate/disable/<int:id>')
# @login_required
# #@permission_required(Permission.MODERATE_COMMENTS)
# def moderate_disable(id):
#     comment = Comment.query.get_or_404(id)
#     comment.disabled = True
#     db.session.add(comment)
#     return redirect(url_for('.moderate',
#                             page=request.args.get('page', 1, type=int)))

# @main.route('/about')
# def about():
#     explain= [['前端框架','Bootstrap'],['服务器','Apache+mod_wsgi'],['图形库','Echarts'],['后端框架','python2.7+Flask'],
#               ['数据库','SQLite3'],['ORM','flask-sqlalchemy'],['','']]
#     return render_template('about.html',explain=explain)



@main.route('/_data', methods=['GET', 'POST'])
#@login_required
def _data():
    data = json.loads(request.form.get('data'))
    for k,v in data.items():
        #效率不高，切连接数过高，后期可以替换更新语句
        if v['deliver_date']:
           deliver_date=datetime.datetime(*time.strptime(v['deliver_date'],'%Y-%m-%d')[:3])
        else:
           deliver_date=None

        if v['arrival_date']:
           arrival_date=datetime.datetime(*time.strptime(v['arrival_date'],'%Y-%m-%d')[:3])
        else:
           arrival_date=None

        db.session.query(U8).filter(U8.id == k).update(\
            {U8.remarks: v["remarks"],U8.received:v['received'],U8.deliver_date :deliver_date ,U8.arrival_date : arrival_date})
    db.session.commit()
    return str("success")

@main.route('/process_order', methods=['GET', 'POST'])
@login_required
def process_order():
    page = request.args.get('page', 1, type=int)
    pagination = U8.query.filter_by(supplier=current_user.company_name).filter(U8.arrival_date==None).order_by(U8.id) \
        .paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    u8s = pagination.items
    count = U8.query.filter_by(supplier=current_user.company_name).filter(U8.arrival_date == None).order_by(U8.id).count()

    return render_template('process_order.html',data=u8s,pagination=pagination,count=count)

@main.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    page = request.args.get('page', 1, type=int)

    pagination = U8.query.filter_by(supplier=current_user.company_name).filter(U8.arrival_date!= None).order_by(U8.id) \
        .paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)

    u8s = pagination.items
    return render_template('view.html',data=u8s,pagination=pagination)

@main.route('/query', methods=['GET', 'POST'])
#@login_required
def query():

    if request.method == 'POST':
        try:
            materialName = request.form['name'].strip().split()
            u8s=U8.query.filter_by(up_code=materialName[0].zfill(10)).filter_by(stock_code=materialName[1].upper()).all()
            print u8s
            return render_template('query.html', data=u8s)
        except:
            u8s=[]
            flash("输入信息错误")
    else:
        u8s = []
        flash("未找到任何信息")

    return render_template('query.html')

@main.route('/__data__', methods=['GET', 'POST'])
#@login_required
def __data__():

        if not request.json :
            abort(400)
        data=request.json
        data=json.loads(data)
        print data
        conn = sqlite3.connect(r'./data-dev.sqlite')  #
        cur = conn.cursor()  # 建立游标对象
        cur.executemany('insert into u8s(date ,supplier, up_code,order_code,stock_code,material_name, \
                            model ,unit ,number ,price) values (?,?,?,?,?,?,?,?,?,?)', data)
        # cur.execute('select * from u8s')
        # print cur.fetchall()
        conn.commit()
        return flask.jsonify({'status': "success"}), 201

# @main.route('/data_hello')
# def data_hello():
#         a={'name':'hello world','name2':'hello world2'}
#         print a
#         return flask.jsonify(a)
#         return json.dumps(a)

