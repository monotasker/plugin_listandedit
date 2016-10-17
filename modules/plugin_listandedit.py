#! /usr/bin/python
# -*- coding: utf-8 -*-

import ast
from gluon import LOAD, current, A, URL, SQLFORM, redirect, SPAN
from gluon.storage import Storage
from icu import Locale, Collator
from importlib import import_module
from operator import itemgetter
import os
from pprint import pprint
import sys

# CSS imported directly into framework.less
# response.files.append(URL('static', 'plugin_listandedit/plugin_listandedit.css'))


def plugin_listandedit():
    '''
    Public interface method to call in views in order to embed the
    plugin_listandedit widget.
    '''
    return LOAD('plugin_listandedit', 'widget.load', ajax=True)


class ListAndEdit(object):
    """
    """

    def _get_rowlist(self, tablename, orderby, restrictor, collation):
        """
        Return a web2py rows object with the db rows for filtered list items.

        """
        db = current.db
        flash = ''
        rowlist = []
        orderby = orderby[0] if isinstance(orderby, list) else orderby

        if tablename not in db.tables():
            flash = '''Sorry, you are trying to list
                    entries from a table that does not exist in the database.'''
        else:
            tb = db[tablename]
            if restrictor:
                # print 'filtering on restrictor'
                for k, v in restrictor.items():
                    filter_select = db(tb[k] == v)._select(tb.id)
                    myrows = db(tb.id.belongs(filter_select)
                                ).select(orderby=~tb[orderby])
            else:
                # print 'no restrictor'
                myrows = db().select(tb.ALL, orderby=~tb[orderby])
        rowlist = myrows.as_list()

        if collation:
            myloc = Locale(collation)
            coll = Collator.createInstance(myloc)
            rowlist = sorted(rowlist, key=itemgetter(orderby), cmp=coll.compare)

        return rowlist, flash

    def _get_params(self, rargs, rvars):
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
            if 'orderby' in rvars:
                orderby = rvars['orderby'].split('|')
        except ValueError:
            pass

        # get filtering values if any
        if 'restrictor' in rvars:
            restr = rvars['restrictor']
            # convert the string from the URL to a python dictionary object
            restrictor = ast.literal_eval(restr)
        else:
            restrictor = None

        # get collation locale if any
        if 'collation' in rvars and rvars['collation'] != 'None':
            collation = rvars['collation']
        else:
            collation = None

        if 'postprocess' in rvars and rvars['postprocess'] != 'None':
            postprocess = rvars['postprocess']
        else:
            postprocess = None

        return tablename, orderby, restrictor, collation, postprocess

    def _get_listitems(self, rowlist, tablename, orderby, restrictor,
                       collation, rvars, postprocess):
        """
        Build actual html list of links for listpane.

        rowlist: web2py rows object containing db row data for list items
        tablename: string giving name of the db table to which the items belong
        orderby: string giving name of the field on which to order items
        restrictor: dict of fieldnames and allowed values to use for filtering items

        """
        db = current.db
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
                       'collation': collation,
                       'postprocess': postprocess
                       }
            vardict.update(rvars)

            i = A(listformat, _href=URL('plugin_listandedit', 'edit.load',
                                        args=[tablename, r.id],
                                        vars=vardict),
                 _class='plugin_listandedit_list',
                 cid='viewpane')
            listset.append(i)
        return listset

    def itemlist(self, rargs=None, rvars=None):
        """
        """
        tablename, orderby, restrictor, collation, postprocess \
            = self._get_params(rargs, rvars)
        print 'postprocess is', postprocess
        rowlist, flash = self._get_rowlist(tablename, orderby, restrictor,
                                           collation)
        listset = self._get_listitems(rowlist, tablename, orderby, restrictor,
                                      collation, rvars, postprocess)
        return listset, flash, tablename, orderby, restrictor

    def _myform(self, formargs, deletable=True, showid=True, formstyle='ul',
                dbio=True):
        """
        Change in subclass to alter the form.
        """
        form = SQLFORM(*formargs,
                       separator='',
                       deletable=deletable,
                       showid=showid,
                       formstyle=formstyle)
        return form

    def _post_process(self, formvars, postprocess):
        """
        Execute dynamically imported code on form vars after main process() method.
        """
        returnval = None
        postprocess = ast.literal_eval(postprocess)
        if postprocess and 'module' in postprocess.keys():

            # allow imports from modules and site-packages
            dirs = os.path.split(__file__)[0]
            appname = dirs.split(os.path.sep)[-2]
            modules_path = os.path.join('applications', appname, 'modules')
            if modules_path not in sys.path:
                sys.path.append(modules_path)  # imports from app modules folder

            mod = import_module(postprocess['module'])
            if 'func' in postprocess.keys():
                myfunc = getattr(mod, postprocess['func'])
                returnval = myfunc(**formvars)

        return returnval

    def editform(self, rargs=None, rvars=None):
        """
        """
        db = current.db

        flash = ''
        rjs = ''
        duplink = ''
        default_vars = {}

        if rargs is not None:
            tablename = rargs[0]
            showid = rvars['showid'] or True
            dbio = False if 'dbio' in rvars.keys() and rvars['dbio'] == 'False' else True
            formstyle = rvars['formstyle'] or 'ul'
            deletable = rvars['deletable'] or True
            copylabel = rvars['copylabel'] or SPAN(_class='glyphicon glyphicon-file')
            orderby = rvars['orderby'] or 'id'
            restrictor = rvars['restrictor'] or None
            collation = rvars['collation'] or None
            postprocess = rvars['postprocess'] or None

            if len(rargs) > 1:  # editing specific item
                rowid = rargs[1]
                formname = '{}/{}'.format(tablename, rowid)
                formargs = [db[tablename], rowid]

                # create a link for adding a new row to the table
                duplink = A(copylabel,
                            _href=URL('plugin_listandedit',
                                      'dupAndEdit.load',
                                      args=[tablename, rowid],
                                      vars=rvars),
                            _class='plugin_listandedit_duplicate',
                            cid='viewpane')

            elif len(rargs) == 1:  # creating new item
                formname = '{}/create'.format(tablename)
                default_vars = {k: v for k, v in rvars.iteritems()
                                if hasattr(db[tablename], k)}
                formargs = [db[tablename]]

            form = self._myform(formargs,
                                deletable=deletable,
                                showid=showid,
                                formstyle=formstyle)
            # print {'default_vars': default_vars}
            # for k in default_vars: form.vars.setitem(k, default_vars[k])
            for k in default_vars: form.vars[k] = default_vars[k]

            # FIXME: ajaxselect field values have to be added manually
            # FIXME: this check will fail if ajaxselect widget is for field indx[1]
            # if db[tablename].fields[1] in rvars.keys():
            #     extras = [f for f in db[tablename].fields
            #               if f not in form.vars.keys()]
            #     for e in extras:
            #         form.vars[e] = rvars[e] if e in rvars.keys() \
            #             else ''
            #     if 'id' in form.vars.keys() and form.vars['id'] in (None, ''):
            #         del(form.vars['id'])
            # else:
            #     pass
            # print 'form vars in editform ---------------------------------'
            # pprint(form.vars)

            if form.process(formname=formname, dbio=dbio).accepted:
                flash = ''
                if postprocess and postprocess not in ['none', 'None']:
                    flash += '{} '.format(self._post_process(form.vars, postprocess))
                if dbio:
                    flash += 'The changes were recorded successfully.'

                # either redirect or refresh the list pane
                if 'redirect' in rvars and 'True' == rvars['redirect']:
                    redirect(URL(rvars['redirect_c'], rvars['redirect_a']))
                else:
                    the_url = URL('plugin_listandedit', 'itemlist.load',
                                  args=[tablename], vars={'orderby': orderby,
                                                          'restrictor': restrictor,
                                                          'collation': collation,
                                                          'postprocess': postprocess})
                    rjs = "window.setTimeout(web2py_component('{}', " \
                          "'listpane'), 500);".format(the_url)
            elif form.errors:
                print '\n\nlistandedit form errors:'
                pprint({k: v for k, v in form.errors.iteritems()})
                print '\n\nlistandedit form vars'
                pprint({k: v for k, v in form.vars.iteritems()})
                print '\n\nlistandedit request vars'
                pprint({k: v for k, v in rvars.iteritems()})
                flash = 'Sorry, there was an error processing ' \
                                'the form. The changes have not been recorded.'

            else:
                pass

        else:
            flash = 'Sorry, you need to specify a type of record before' \
                             'I can list the records.'
            form = None

        return form, duplink, flash, rjs

    def dupform(self, rargs=None, rvars=None, copylabel=None,
                deletable=True, showid=True, dbio=True, formstyle='ul'):
        """
        """
        db = current.db
        rjs = ''
        flash = ''
        duplink = ''
        tablename = rargs[0]
        rowid = rargs[1]
        orderby = rvars['orderby'] or 'id'
        restrictor = rvars['restrictor'] or None
        collation = rvars['collation'] or None
        postprocess = rvars['postprocess'] or None
        copylabel = copylabel if copylabel else 'Make a copy of this record'
        dbio = False if 'dbio' in rvars.keys() and rvars['dbio'] == 'False' else True

        # create a link for adding a new row to the table
        duplink = A(copylabel,
                    _href=URL('plugin_listandedit',
                                'dupAndEdit.load',
                                args=[tablename, rowid],
                                vars=rvars),
                    _class='plugin_listandedit_duplicate',
                    cid='viewpane')

        formname = '{}/{}/dup'.format(tablename, rowid)

        src = db(db[tablename].id == rowid).select().first()
        form = SQLFORM(db[tablename],
                       separator='',
                       deletable=deletable,
                       showid=showid,
                       formstyle=formstyle)

        for v in db[tablename].fields:
            # on opening populate duplicate values
            form.vars[v] = src[v] if v != 'id' and v in src else None
            # FIXME: ajaxselect field values have to be added manually
            if db[tablename].fields[1] in rvars.keys():  # on submit add ajaxselect values
                extras = [f for f in db[tablename].fields
                        if f not in form.vars.keys()]
                for e in extras:
                    form.vars[e] = rvars[e] if e in rvars.keys() else ''
        del form.vars['id']
        # print 'form vars ========================================='
        # pprint(form.vars)

        if form.process(formname=formname, dbio=dbio).accepted:
            db.commit()
            #print 'accepted form ================================='
            the_url = URL('plugin_listandedit', 'itemlist.load',
                          args=[tablename], vars={'orderby': orderby,
                                                  'restrictor': restrictor,
                                                  'collation': collation,
                                                  'postprocess': postprocess})
            rjs = "web2py_component('{}', 'listpane');".format(the_url)
            if dbio:
                flash = 'New record successfully created.'
        elif form.errors:
            print 'listandedit form errors:', [e for e in form.errors]
            print 'listandedit form vars:', form.vars
            flash = 'Sorry, there was an error processing '\
                            'the form. The new record has not been created.'
        else:
            pass

        return form, duplink, flash, rjs
