#!/bin/bash
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)

set -e

svn checkout http://oyoyo.googlecode.com/svn/trunk/oyoyo/oyoyo -r55

#git submodule update --init   # won't work, repo taken down by whatsapp. workaround below:
wget https://github.com/stenyak/yowsup/archive/master.zip
unzip master.zip
rm master.zip
mv yowsup-master yowsup.git
