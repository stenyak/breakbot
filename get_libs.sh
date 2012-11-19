#!/bin/bash
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
svn checkout http://oyoyo.googlecode.com/svn/trunk/oyoyo/oyoyo -r55
git clone https://github.com/tgalal/yowsup.git yowsup.git
ln -s yowsup.git/src/Yowsup .
cd yowsup.git
    git checkout c5d656edce0373c97352be283d27f794df40b4c1
cd ..
