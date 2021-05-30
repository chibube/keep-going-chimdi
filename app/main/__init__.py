#this is a blueprint, a blueprint is similar to an application but the diff is that
#routes and error handlers defined here remain dormant until they are registered in the
#application

from flask import Blueprint

main = Blueprint('main', __name__) #blueprints are created by instantiating an object of
#class Blueprint. the constructor for this class takes in 2 arg.: the blueprint name &
# the module or package where the blueprint is located.

#the "." in thi statement reps the current package
from . import views, errors #importing these modules cause them to be associated with
#the Blueprint
#Note: it is important to note that the modules are imported at the bottom of the
#app/main/__init__.py script to avoid errors due to circular dependencies. In this
# particular example the problem is that app/main/views.py and app/main/errors.py in
#turn are going to import the main blueprint object, so the imports are going to fail
#unless the circular reference occurs after the main is defined.