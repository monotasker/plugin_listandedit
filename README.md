# plugin_listandedit

Copyright Ian W. Scott, 2012 (scottianw@gmail.com)
Licensed as free software under the GPL 3.0 license.

## Overview

A widget plugin for the web2py framework, providing a large interface to simultaneously list, create and edit records from a 
given database table

## Use

Where you want the widget to appear, simply add the following to your web2py template:

    {{=LOAD('plugin_listandedit', 'widget.load', args=request.args, vars=request.vars, ajax=False, ajax_trap=True)}} 
    
Note that this snippet passes the arguments and variables from the parent view on to the plugin_listandedit controller. If 
you do not want this, simply replace request.args with a list of arguments and replace request.vars with a dictionary 
of variables.

## Installation

- create folder appname/plugins
- place plugin_framework folder in this new plugins folder
- create symlinks from plugin files to application directories:

    cd [web2py_folder]/applications/myapp  
    ln -s ../plugins/plugin_listandedit/views/plugin_listandedit views/plugin_listandedit  
    ln -s ../plugins/plugin_listandedit/models/plugin_listandedit.py models/plugin_listandedit.py  
    ln -s ../plugins/plugin_listandedit/static/plugin_listandedit static/plugin_framework  
    ln -s ../plugins/plugin_listandedit/controllers/plugin_listandedit.py controllers/plugin_listandedit.py  
    
** note that the relative addresses allow the symbolic links to work even across systems where the web2py directory is in 
different locations.