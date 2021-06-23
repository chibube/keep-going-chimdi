from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

#flask-login properties can be implemented directly in the model class, but as an easier alternative
#flask-login provides a UserMixin class that has default implementation that are appropriate for most cases.
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    @property #Password is a write only property (this is called a function decorator) and you can chain multiple to 1 func
    #when 2 or more decorators are used in 1 function, each decorator only affects those that are blow it in addition to
    #the target function.
    def password(self):
        raise AttributeError('password is not a readable attribute') #any attempt to read the password property raises an error

    @password.setter #this is a setter method that calls werkzeug's gen_password function, it takes the user's password and encrypts it
    def password(self, password):
        self.password_hash = generate_password_hash(password)#here the password hash is generated and passed into the db model above for each user

    def verify_password(self, password):#takes a password & passes it to werkzeug's
        #check_password_hash() function for verification against the hashed ver. stored in the User model
        return check_password_hash(self.password_hash, password)

    #this function verifies the token and, if valid, sets the new confirmed attribute in the user
    #model
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id: #it also checks that the id from the token matches the logged in user
            return False
        self.confirmed = True
        db.session.add(self)
        return True
#this method generates a token with a default validity time of one hour(see pag 119, p3&4)
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def __repr__(self):
        return '<User %r>' % self.username



@login_manager.user_loader #this decorator registers the function with Flask-Login, which will call it when it needs to retrieve information about the logged-in user.
def load_user(user_id):
    return User.query.get(int(user_id)) #user function will be passed as a string this converts it to an integer
    #before passing it to flask-SQLAlchemy query that loads the user.