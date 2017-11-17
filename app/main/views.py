#coding:utf-8
from app import db
from . import main
from ..models import User,Role,Permission,Post
from .forms import EditProfileForm,EditProfileAdminForm,PostForm
from ..decorators import admin_required,premission_required
from flask_login import login_required,current_user
from flask import render_template, abort, url_for, flash, redirect, request, current_app


@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination)


#展示个人信息页面路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user,posts=posts,pagination=pagination)

#普通用户资料编辑路由
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me  = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'您的资料已更新.')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

#管理员编辑资料路由
@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
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
        db.session.commit()
        flash(u'用户资料已更新.')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash(u'你的文章已修改.')
        return redirect(url_for('post',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

#关注
@main.route('/follow/<username>')
@login_required
@premission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户.')
        return redirect(url_for('mian.index'))
    if current_user.is_following(user):
        flash(u'你已经关注了他.')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    flash(u'你已经将%s加入关注名单.' % username)
    return redirect(url_for('main.user',username=username))

#取消关注
@main.route('/unfollow/<username>')
@login_required
@premission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash(u'您还没有关注该用户.')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash(u'您已取消对%s的关注.' % username)
    return redirect(url_for('main.user',username=username))

#关注列表
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户.')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title='Followers of',endpoint='.followers',
                           pagination=pagination,follows=follows)

#被关注列表
@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户.')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.pagination(page,per_page=current_app.config['FLASKY_FOLLOWES_PER_PAGE'],
                                          error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title='Followed by',endpoint='.followed_by',
                           pagination=pagination,follows=follows)

