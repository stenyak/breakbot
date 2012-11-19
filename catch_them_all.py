# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from log import error

def catch_them_all(function):
    """ Decorator that logs all exceptions thrown by the called function, and allows to continue.
    Can be useful when used as wrapper for callbacks whose execution you don't fully control """
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            error("Exception in function %s" % function.__name__)
    return wrapper
