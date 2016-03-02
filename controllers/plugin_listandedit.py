#! /usr/bin/python
# coding: utf8

if 0:
    from gluon import current, URL, A, SPAN
    response = current.response
    request = current.request
    db = current.db
    session = current.session
from plugin_listandedit import ListAndEdit
from pprint import pprint

response.files.append(URL('static', 'css/plugin_listandedit.css'))


def itemlist():
    """
    This plugin creates a large widget to display, edit, and add entries
    to one database table.

    LIST FORMAT
    By default the table rows are listed using either the "format" property
    of the table definition in the db model (if their is one), or the contents
    of the first table field (after the auto-generated id).

    ARGUMENTS
    Takes one required argument, the name of the table to be listed.

    A second optional argument provides the name of a field by which to order
    the list.

    VARIABLES
    An optional variable "restrictor" can be used to filter the displayed
    records. This variable must be a dictionary in which the keys are the names
    of fields in the table and the values are the values to be allowed in those
    fields when generating the list.
    """
    lae = ListAndEdit()
    listset, flash, tname, orderby, restrictor = lae.itemlist(rargs=request.args,
                                                              rvars=request.vars)
    if flash:
        response.flash = flash
    return {'listset': listset}


def widget():
    """
    This plugin creates a large widget to display, edit, and add entries
    to one database table.

    LIST FORMAT
    By default the table rows are listed using either the "format" property
    of the table definition in the db model (if their is one), or the contents
    of the first table field (after the auto-generated id).

    ARGUMENTS
    Takes one required argument, the name of the table to be listed.

    A second optional argument provides the name of a field by which to order
    the list.

    VARIABLES
    An optional variable "restrictor" can be used to filter the displayed
    records. This variable must be a dictionary in which the keys are the names
    of fields in the table and the values are the values to be allowed in those
    fields when generating the list.
    """
    lae = ListAndEdit()
    itemlist, flash, tname, orderby, restrictor = lae.itemlist(rargs=request.args,
                                                               rvars=request.vars)

    adder = A(SPAN(_class='glyphicon glyphicon-plus'),
              _href=URL('plugin_listandedit', 'edit.load',
                        args=[tname],
                        vars=request.vars),
              _class='plugin_listandedit_addnew badge badge-success',
              cid='viewpane')

    return {'listset': itemlist,
            'tablename': tname,
            'restrictor': restrictor,
            'orderby': orderby,
            'adder': adder}


def dupAndEdit():
    """Create and process a form to insert a new record, pre-populated
    with field values copied from an existing record."""
    form, duplink, flash, rjs = ListAndEdit().dupform(rargs=request.args,
                                                      rvars=request.vars)
    if flash:
        response.flash = flash
    if rjs:
        response.js = rjs

    return {'form': form, 'duplink': duplink}


def edit():
    """create and proccess the form to either edit and update one of the listed
    records or insert a new record into the db table.

    returns a dictionary with two values:
        form: a web2py SQLFORM() helper object
        duplink: a web2py A() helper that will trigger the dupAndEdit()
            function of this controller, opening a form to insert a new record
            and pre-populating it with data copied from the current record.
    """
    # print 'controller edit:: request.vars is --------------------------'
    # pprint(request.vars)
    form, duplink, flash, rjs = ListAndEdit().editform(rargs=request.args,
                                                        rvars=request.vars)
    if flash:
        response.flash = flash
    if rjs:
        response.js = rjs

    return {'form': form, 'duplink': duplink}
