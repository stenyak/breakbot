# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from timestamp import Timestamp
import ntpath
import inspect
import traceback
import sys

def log(text, timestamp = None):
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)
    frame,filename,line_number,function_name,lines,index = inspect.getouterframes(inspect.currentframe())[2] # log caller stack
    filename = path_leaf(filename)
    _,_,_,log_type,_,_ = inspect.getouterframes(inspect.currentframe())[1] # log function (info, error...)
    log_type = log_type[0].upper() * 2 # II for info, EE for error...
    if timestamp is None:
        timestamp = Timestamp()
    print "%s %s %s:%s: %s" %(timestamp.to_human_str(), log_type, filename, line_number, text)
def info(text):
    log(text)
def error(text):
    t, v, tb = sys.exc_info()
    if t is None:
        log(text)
    else:
        time = Timestamp()
        log("%s (%s):" %(text, t.__name__), time)
        lines = traceback.format_exception(t, v, tb)
        lines = [": ".join(line.split("\n")) for line in traceback.format_exception(t, v, tb)]
        for line in lines[1:-1]:
            log(">%s" %line, time)
