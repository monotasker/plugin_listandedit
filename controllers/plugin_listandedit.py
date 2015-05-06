#! /usr/bin/python
# coding: utf8

if 0:
    from gluon import current, URL, SQLFORM, A
    response = current.response
    request = current.request
    db = current.db
    session = current.session
from gluon.storage import Storage
import ast
# import traceback
from gluon import redirect
from pprint import pprint
# from plugin_utils import islist
from operator import itemgetter
from icu import Locale, Collator

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

    tablename, orderby, restrictor, collation = _get_params(request.args, request.vars)

    rowlist = _get_rowlist(tablename, orderby, restrictor, collation)
    listset = _get_listitems(rowlist, tablename, orderby, restrictor, collation)

    return {'listset': listset}


def _get_rowlist(tablename, orderby, restrictor, collation):
    """
    Return a web2py rows object with the db rows for filtered list items.

    """
    rowlist = []
    orderby = orderby[0] if isinstance(orderby, list) else orderby

    if tablename not in db.tables():
        response.flash = '''Sorry, you are trying to list
        entries from a table that does not exist in the database.'''
    else:
        tb = db[tablename]
        if restrictor:
            print 'filtering on restrictor'
            for k, v in restrictor.items():
                filter_select = db(tb[k] == v)._select(tb.id)
                rowlist = db(tb.id.belongs(filter_select)
                             ).select(orderby=~tb[orderby])
        else:
            print 'no restrictor'
            myrows = db().select(tb.ALL, orderby=~tb[orderby])
    rowlist = myrows.as_list()

    if collation:
        myloc = Locale('el')
        coll = Collator.createInstance(myloc)
        rowlist = sorted(rowlist, key=itemgetter(orderby), cmp=coll.compare)

    return rowlist


def _get_params(rargs, rvars):
    """
    Return the tablename, orderby and restrictor parameters for the list items.

    rargs: A list of strings giving url arguments
    rvars: A dictionary of url named parameters
    """
    # get table to be listed
    tablename = rargs[0]

    # allow ordering of list based on values in any field
    orderby = 'id'
    try:
        if 'orderby' in request.vars:
            orderby = rvars['orderby'].split('|')
    except ValueError:
        pass

    # get filtering values if any
    if 'restrictor' in request.vars:
        restr = rvars['restrictor']
        # convert the string from the URL to a python dictionary object
        restrictor = ast.literal_eval(restr)
    else:
        restrictor = None

    # get collation locale if any
    if 'collation' in request.vars:
        collation = rvars['collation']
    else:
        collation = None

    print 'tablename:', tablename
    print 'orderby:', orderby
    print 'restrictor:', restrictor

    return tablename, orderby, restrictor, collation


def _get_listitems(rowlist, tablename, orderby, restrictor, collation):
    """
    Build actual html list of links for listpane.

    rowlist: web2py rows object containing db row data for list items
    tablename: string giving name of the db table to which the items belong
    orderby: string giving name of the field on which to order items
    restrictor: dict of fieldnames and allowed values to use for filtering items

    """
    listset = []
    for r in rowlist:
        r = Storage(r)
        fieldname = db[tablename].fields[1]
        # use format string from db table definition to list entries (if
        # available)
        fmt = db[tablename]._format
        if fmt:
            listformat = fmt(r) if callable(fmt) else fmt % r
        else:
            listformat = r[fieldname]

        vardict = {'tablename': tablename,
                   'orderby': orderby,
                   'restrictor': restrictor,
                   'collation': collation
                   }
        vardict.update(request.vars)

        i = A(listformat, _href=URL('plugin_listandedit', 'edit.load',
                                    args=[tablename, r.id],
                                    vars=vardict),
              _class='plugin_listandedit_list',
              cid='viewpane')
        listset.append(i)

    return listset


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
    # TODO: not clear whether appending file here works after page load
    # I think I would have to append file in the parent view.
    # response.files.append(URL('static',
    # 'plugin_listandedit/plugin_listandedit.js'))

    tablename, orderby, restrictor, collation = _get_params(request.args, request.vars)
    rowlist = _get_rowlist(tablename, orderby, restrictor, collation)
    html_list = _get_listitems(rowlist, tablename, orderby, restrictor, collation)

    adder = A(u'\u200b', _href=URL('plugin_listandedit', 'edit.load',
                                   args=[tablename],
                                   vars=request.vars),
            _class='plugin_listandedit_addnew icon-plus badge badge-success',
            cid='viewpane')

    return dict(listset=html_list, adder=adder,
                tablename=tablename, restrictor=restrictor, orderby=orderby)


def dupAndEdit():
    """Create and process a form to insert a new record, pre-populated
    with field values copied from an existing record."""
    tablename = request.args[0]
    rowid = request.args[1]
    orderby = request.vars['orderby'] or 'id'
    restrictor = request.vars['restrictor'] or None
    collation = request.vars['collation'] or None
    formname = '%s/%s/dup' % (tablename, rowid)

    src = db(db[tablename].id == rowid).select().first()
    form = SQLFORM(db[tablename], separator='', showid=True, formstyle='ul')

    for v in db[tablename].fields:
        # on opening populate duplicate values
        form.vars[v] = src[v] if v != 'id' and v in src else None
        # FIXME: ajaxselect field values have to be added manually
        if db[tablename].fields[1] in request.vars.keys():  # on submit add ajaxselect values
            extras = [f for f in db[tablename].fields
                      if f not in form.vars.keys()]
            for e in extras:
                form.vars[e] = request.vars[e] if e in request.vars.keys() \
                    else ''
    del form.vars['id']
    print 'form vars ========================================='
    pprint(form.vars)

    if form.process(formname=formname).accepted:
        db.commit()
        print 'accepted form ================================='
        the_url = URL('plugin_listandedit', 'itemlist.load',
                      args=[tablename], vars={'orderby': orderby,
                                              'restrictor': restrictor,
                                              'collation': collation})
        response.js = "web2py_component('%s', " \
                      "'listpane');" % the_url
        response.flash = 'New record successfully created.'
    elif form.errors:
        print 'listandedit form errors:', [e for e in form.errors]
        print 'listandedit form vars:', form.vars
        response.flash = 'Sorry, there was an error processing '\
                         'the form. The new record has not been created.'
    else:
        pass

    return dict(form=form)


def edit():
    """create and proccess the form to either edit and update one of the listed
    records or insert a new record into the db table.

    returns a dictionary with two values:
        form: a web2py SQLFORM() helper object
        duplink: a web2py A() helper that will trigger the dupAndEdit()
            function of this controller, opening a form to insert a new record
            and pre-populating it with data copied from the current record.
    """
    duplink = ''
    default_vars = {}
    if request.args is not None:
        tablename = request.args[0]
        orderby = request.vars['orderby'] or 'id'
        restrictor = request.vars['restrictor'] or None
        collation = request.vars['collation'] or None

        if len(request.args) > 1:  # editing specific item
            rowid = request.args[1]
            formname = '%s/%s' % (tablename, rowid)
            rargs = [db[tablename], rowid]

            # create a link for adding a new row to the table
            duplink = A('Make a copy of this record',
                        _href=URL('plugin_listandedit',
                                'dupAndEdit.load',
                                args=[tablename, rowid],
                                vars=request.vars),
                        _class='plugin_listandedit_duplicate', cid='viewpane')

        elif len(request.args) == 1:  # creating new item
            formname = '%s/create' % (tablename)
            default_vars = {k: v for k, v in request.vars.iteritems()
                            if hasattr(db[tablename], k)}
            rargs = [db[tablename]]

        form = SQLFORM(*rargs, separator='',
                deletable=True,
                showid=True,
                formstyle='ul')
        # print {'default_vars': default_vars}
        # for k in default_vars: form.vars.setitem(k, default_vars[k])
        for k in default_vars: form.vars[k] = default_vars[k]

        # FIXME: ajaxselect field values have to be added manually
        # FIXME: this check will fail if ajaxselect widget is for field indx[1]
        if db[tablename].fields[1] in request.vars.keys():
            extras = [f for f in db[tablename].fields
                      if f not in form.vars.keys()]
            for e in extras:
                form.vars[e] = request.vars[e] if e in request.vars.keys() \
                    else ''
            if 'id' in form.vars.keys() and form.vars['id'] in (None, ''):
                del(form.vars['id'])
        else:
            pass

        if form.process(formname=formname).accepted:
            response.flash = 'The changes were recorded successfully.'
            if 'redirect' in request.vars and 'True' == request.vars['redirect']:
                redirect(URL(request.vars['redirect_c'], request.vars['redirect_a']))
            else:
                the_url = URL('plugin_listandedit', 'itemlist.load',
                              args=[tablename], vars={'orderby': orderby,
                                                      'restrictor': restrictor,
                                                      'collation': collation})
                response.js = "window.setTimeout(" \
                              "web2py_component('{}', " \
                              "'listpane'), 500);".format(the_url)
        elif form.errors:
            print '\n\nlistandedit form errors:'
            pprint({k: v for k, v in form.errors.iteritems()})
            print '\n\nlistandedit form vars'
            pprint({k: v for k, v in form.vars.iteritems()})
            print '\n\nlistandedit request vars'
            pprint({k: v for k, v in request.vars.iteritems()})
            response.flash = 'Sorry, there was an error processing ' \
                             'the form. The changes have not been recorded.'

        else:
            print '\n\nno errors but form not processed:', form.vars
            pass

    else:
        response.flash = 'Sorry, you need to specify a type of record before' \
                         'I can list the records.'
        form = None

    return {form: form, duplink: duplink}
