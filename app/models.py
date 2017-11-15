#coding:utf-8

import hashlib
from . import db
from . import login_manager
from flask_login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as  Serializer
from flask import current_app, request
from datetime import datetime


class User(UserMixin,db.Model):
    '''
    用户信息
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post',backref='author',lazy='dynamic')

	
    def __init__(self,**kwargs):
        '''
        定义默认的用户角色
        '''
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(permissions='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    '''
    通过generate_fake方法添加虚拟数据，生产环境非必须
    '''
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password='password',
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

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
            hash = self.avatar_hash or self.gravatar_hash()
            return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,
                    hash=hash,size=size,default=default,rating=rating)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions
	
    def is_administrator(self):
        return self.can(Permission.ADMIN)
	
    @property
    def password(self):
        raise AttributeError('password is not a readable attribut')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    #生成确认令牌
    def generate_confirmation_token(self,expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in= expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):
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

    def generate_reset_token(self,expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'reset':self.id})

    def reset_password(self,token,new_password):
        s= Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email = new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser



class Role(db.Model):
    '''
    用户角色:
    匿名：0x00
    普通用户 User：0x07
    协管员 Moderator：0x0f
    管理员 Administrator：0xff
    '''
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __init__(self,**kwargs):
        super(Role,self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
			'User':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE],
			'Moderator':[Permission.FOLLOW,Permission.COMMENT,
						 Permission.WRITE,Permission.MODERATE],
			'Administrator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,
                             Permission.MODERATE,Permission.ADMIN]
		}
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permissions = perm
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def has_permission(self,perm):
        return self.permissions & perm == perm

    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0
	
    def __repr__(self):
        return '<Role %r>' % self.name
	
class Permission:
    '''
    权限常量：
	FOLLOW = 1             关注用户
    COMMENT = 2            在他人的文章中评论
    WRITE = 4     写原创文章
    MODERATE = 8  管理他人发表的评论
    ADMIN = 16         管理员权限
	'''
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))

#文章模型
class Post(db.Model):
    '''
    文章模型
    '''
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    '''
    通过generate_fake方法添加虚拟数据，生产环境非必须
    '''
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint

        import forgery_py
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                 timestamp=forgery_py.date.date(True),
                 author=u)
            db.session.add(p)
            db.session.commit()