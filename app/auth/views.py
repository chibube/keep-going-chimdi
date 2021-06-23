#this module imports the bluepring and defines the routes associated with authentication
#using its route decorator
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.blueprint != 'auth'\
        and request.endpoint != 'static':
      return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST']) #when the request is of type GET, the view function just renders the
#template, which in turn displays the form. When the form is submitted in a POST request, Flask-WTF's validate_on_submit
def login():
    form = LoginForm() #Pass the Loginform with the field in a variable
    if form.validate_on_submit(): #if all the fields get validated
        user = User.query.filter_by(email=form.email.data).first()#pass the email into the usr var
        if user is not None and user.verify_password(form.password.data):#if there alreay exists & their password is ok
            login_user(user, form.remember_me.data)
            next = request.args.get('next')#this redirects the user to the url they were trying to access
            if next is None or not next.startswith('/'): #if they were coming from the login page redirect to home
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)
# flask expects the templates' paths to be relative to the application's templates directory
#blueprints can also be configured to have their own directory for templates.
#When multiple template directories have been configured, the render_template()
#function searches the templates directory configured for the application first,
#and then searches the template directories defined by blueprints.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed: #checks if the logged in user is confirmed and if yes, redirects to homepage
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))