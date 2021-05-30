from flask import Blueprint

#Blueprints are a way to define routes in a global scope after the creation of the
#application has been moved into a factory function.as
#using different blueprints for diff subsystems is a good way to keep your code
#neatly organised.
auth = Blueprint('auth', __name__)
#This bluepring package constructor creates the bluepring and imports routes from
#views

from . import views

#the auth blueprint also has to be attached to the create_app() factory function