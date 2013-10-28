# coding: utf8
import ast
#import traceback
from pprint import pprint
if 0:
    from gluon import current, URL, SQLFORM, A
    response = current.response
    request = current.request
    db = current.db
    session = current.session


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

    #get table to be listed
    tablename = request.args[0]

    #allow ordering of list based on values in any field
    orderby = 'id'
    try:
        if 'orderby' in request.vars:
            orderby = request.vars['orderby']
    except ValueError:
        pass

    #pass that name on to be used as a title for the widget
    #rname = tablename + ' (' + orderby + ')'

    #get filtering values if any
    if 'restrictor' in request.vars:
        restr = request.vars['restrictor']
        # convert the string from the URL to a python dictionary object
        restrictor = ast.literal_eval(restr)
    else:
        restrictor = None

    #check to make sure the required argument names a table in the db
    if not tablename in db.tables():
        response.flash = '''Sorry, you are trying to list
        entries from a table that does not exist in the database.'''
    else:
        tb = db[tablename]
        #select all rows in the table

        #filter that set based on any provided field-value pairs in
        #request.vars.restrictor
        if restrictor:
            for k, v in restrictor.items():
                filter_select = db(tb[k] == v)._select(tb.id)
                rowlist = db(tb.id.belongs(filter_select)).select()
        else:
            rowlist = db().select(tb.ALL, orderby=~tb[orderby])

    # build html list from the selected rows
    listset = []
    for r in rowlist:
        fieldname = db[tablename].fields[1]
        # use format string from db table definition to list entries (if
        #available)
        fmt = db[tablename]._format
        if fmt:
            listformat = fmt(r) if callable(fmt) else fmt % r
        else:
            listformat = r[fieldname]

        vardict = {'tablename': tablename}
        if not vardict is None:
            vardict['restrictor'] = restrictor

        i = A(listformat, _href=URL('plugin_listandedit', 'edit.load',
                                    args=[tablename, r.id],
                                    vars=vardict),
              _class='plugin_listandedit_list',
              cid='viewpane')
        listset.append(i)

    return dict(listset=listset)


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
    tablename = request.args[0]
    orderby = 'id'
    try:
        if 'orderby' in request.vars:
            orderby = request.vars['orderby']
    except ValueError:
        pass

    #pass that name on to be used as a title for the widget
    rname = tablename + ' (' + orderby + ')'

    #get filtering values if any
    if 'restrictor' in request.vars:
        restr = request.vars['restrictor']
        # convert the string from the URL to a python dictionary object
        restrictor = ast.literal_eval(restr)
    else:
        restrictor = None

    #check to make sure the required argument names a table in the db
    if not tablename in db.tables():
        response.flash = '''Sorry, you are trying to list
        entries from a table that does not exist in the database.'''
    else:
        tb = db[tablename]
        #select all rows in the table

        #filter that set based on any provided field-value pairs in
        #request.vars.restrictor
        if restrictor:
            for k, v in restrictor.items():
                filter_select = db(tb[k] == v)._select(tb.id)
                rowlist = db(tb.id.belongs(filter_select)).select()
        else:
            rowlist = db().select(tb.ALL, orderby=~tb[orderby])

    # build html list from the selected rows
    listset = []
    for r in rowlist:
        fieldname = db[tablename].fields[1]
        # use format string from db table definition to list entries (if
        #available)
        if db[tablename]._format:
            try:
                listformat = db[tablename]._format % r
            except:
                listformat = db[tablename]._format(r)
        else:
            listformat = r[fieldname]

        vardict = {'tablename': tablename,
                   'orderby': orderby}
        if not restrictor is None:
            vardict['restrictor'] = restrictor

        i = A(listformat, _href=URL('plugin_listandedit', 'edit.load',
                                    args=[tablename, r.id],
                                    vars=vardict),
              _class='plugin_listandedit_addnew',
              cid='viewpane')
        listset.append(i)

    # create a link for adding a new row to the table
    adder = A(u'\u200b', _href=URL('plugin_listandedit', 'edit.load',
                                   args=[tablename],
                                   vars=request.vars),
            _class='plugin_listandedit_addnew icon-plus badge badge-success',
            cid='viewpane')

    return dict(listset=listset, adder=adder, rname=rname)


def makeurl(tablename, orderby, restrictor):
    rdict = {'orderby': orderby}
    if not restrictor is None:
        rdict['restrictor'] = restrictor
    the_url = URL('plugin_listandedit', 'itemlist.load',
                  args=[tablename], vars=rdict)
    return the_url


def dupAndEdit():
    """Create and process a form to insert a new record, pre-populated
    with field values copied from an existing record."""
    tablename = request.args[0]
    rowid = request.args[1]
    orderby = request.vars['orderby'] or 'id'
    restrictor = request.vars['restrictor'] or None
    formname = '%s/%s/dup' % (tablename, rowid)

    src = db(db[tablename].id == rowid).select().first()
    form = SQLFORM(db[tablename], separator='', showid=True, formstyle='ul')

    for v in db[tablename].fields:
        if v != 'id' and v in src:
            form.vars[v] = src[v]
            #TODO: somehow have the widget refreshed with the pre-populated
            #value. maybe this would work by pre-creating a session value for
            #the new form?
            #somehow test to see if the field is AjaxSelect widget
            #if so, set session value for field
            wrappername = tablename + '_' + v + '_loader'
            session[wrappername] = src[v]

    if form.process(formname=formname).accepted:
        the_url = makeurl(tablename, orderby, restrictor)
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
    print '\n starting controllers/plugin_listandedit edit()'

    tablename = request.args[0]
    orderby = request.vars['orderby'] or 'id'
    restrictor = request.vars['restrictor'] or None
    duplink = ''
    if len(request.args) > 1:
        rowid = request.args[1]
        formname = '%s/%s' % (tablename, rowid)

        #TODO: Set value of "project" field programatically
        form = SQLFORM(db[tablename], rowid, separator='',
                deletable=True,
                showid=True,
                formstyle='ul')
        # FIXME: ajaxselect field value has to be added manually
        if 'id' in request.vars.keys():
            extras = [f for f in db[tablename].fields
                      if f not in form.vars.keys()]
            for e in extras:
                form.vars[e] = request.vars[e] if e in request.vars.keys() \
                    else ''
                print 'adding field', e, ':', form.vars[e]
        #except Exception:
            #print traceback.format_exc(5)
        #for f in ['steps', 'slides', 'map_location', 'npcs', 'tags',
                  #'tags_secondary', 'tags_ahead', 'locations', 'hints',
                  #'instructions']:
        if form.process(formname=formname).accepted:
            the_url = makeurl(tablename, orderby, restrictor)
            response.js = "window.setTimeout(" \
                          "web2py_component('{}', " \
                          "'listpane'), 500);".format(the_url)
            response.flash = 'The changes were recorded successfully.'
            print '\n\nform processed'
            print "listandedit submitted form vars:", form.vars
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
            #TODO: Why is this line being run when a record is first selected?
            print '\n\nform not processed, but no errors'
            pprint({k: v for k, v in form.vars.iteritems()})
            pprint({k: v for k, v in request.vars.iteritems()})
            pass

        # create a link for adding a new row to the table
        duplink = A('Make a copy of this record',
                    _href=URL('plugin_listandedit',
                              'dupAndEdit.load',
                              args=[tablename, rowid],
                              vars=request.vars),
                    _class='plugin_listandedit_duplicate', cid='viewpane')

    elif len(request.args) == 1:
        formname = '%s/create' % (tablename)

        form = SQLFORM(db[tablename], separator='',
                       showid=True,
                       formstyle='ul')
        if form.process(formname=formname).accepted:
            the_url = makeurl(tablename, orderby, restrictor)
            response.js = "web2py_component('%s', 'listpane');" % the_url
            response.flash = 'New record successfully created.'
            print "submitted form vars", form.vars
        elif form.errors:
            print form.vars
            response.flash = 'Sorry, there was an error processing '\
                             'the form. The new record has not been created.'
        else:
            pass

    else:
        response.flash = 'Sorry, you need to specify a type of record before' \
                'I can list the records.'

    return dict(form=form, duplink=duplink)
