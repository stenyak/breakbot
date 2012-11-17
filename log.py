# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from timestamp import Timestamp
import ntpath
import inspect
def info(text):
    def path_leaf(path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)
    frame,filename,line_number,function_name,lines,index=inspect.getouterframes(inspect.currentframe())[1]
    filename = path_leaf(filename)
    print "%s %s:%s: %s" %(Timestamp().to_human_str(), filename, line_number, text)
