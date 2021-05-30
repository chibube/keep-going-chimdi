from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#a diff when writing error handlers inside a blueprint is that if the errorhandler
#decorator is used, the handler will be invoked only for errors that originate in the
#routes defined by the blueprint. To install application wide error handlers, the
#app_errorhandler decorator must be used instead