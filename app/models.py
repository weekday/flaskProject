#coding:utf-8

from . import db
from . import login_manager
from flask_login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as  Serializer
from flask import current_app

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
	
    def __init__(self,**kwargs):
        '''
        定义默认的用户角色
        '''
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).firset()

    def can(self,permissions):
        return self.role is not None and (self.role.permissions)
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
            data = s.loads(token)
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
	
    @staticmethod
    def insert_roles():
        roles = {
			'User':(Permission.FOLLOW | Permission.COMMENT |
				  Permission.WRITE_ARTICLES ,True),
			'Moderator':(Permission.FOLLOW | Permission.COMMENT |
						 Permission.WRITE_ARTICLES |
						 Permission.MODERATE_COMMENTS,False),
			'Administrator':(0xff,False)
		}
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = role[r][0]
            role.default = role[r][1]
        db.session.commit()
		
	
    def __repr__(self):
        return '<Role %r>' % self.name
	
class Permission:
    '''
    权限常量：
	FOLLOW = 0x01             关注用户
    COMMENT = 0x02            在他人的文章中评论
    WRITE_ARTICLES = 0x04     写原创文章
    MODERATE_COMMENTS = 0x08  管理他人发表的评论
    ADMINISTER = 0x80         管理员权限
	'''
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))