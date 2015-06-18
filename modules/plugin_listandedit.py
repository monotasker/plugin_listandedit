from gluon import LOAD, current, A, URL, SQLFORM, redirect
from pprint import pprint

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

    def editform(self, rargs=None, rvars=None, copylabel=None,
                 deletable=True, showid=True, formstyle='ul'):
        """
        """
        db = current.db

        flash = ''
        rjs = ''
        duplink = ''
        default_vars = {}
        copylabel = copylabel if copylabel else 'Make a copy of this record'
        if rargs is not None:
            tablename = rargs[0]
            orderby = rvars['orderby'] or 'id'
            restrictor = rvars['restrictor'] or None
            collation = rvars['collation'] or None

            if len(rargs) > 1:  # editing specific item
                rowid = rargs[1]
                formname = '%s/%s' % (tablename, rowid)
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

            form = SQLFORM(*formargs, separator='',
                           deletable=deletable,
                           showid=showid,
                           formstyle=formstyle)
            # print {'default_vars': default_vars}
            # for k in default_vars: form.vars.setitem(k, default_vars[k])
            for k in default_vars: form.vars[k] = default_vars[k]

            # FIXME: ajaxselect field values have to be added manually
            # FIXME: this check will fail if ajaxselect widget is for field indx[1]
            if db[tablename].fields[1] in rvars.keys():
                extras = [f for f in db[tablename].fields
                          if f not in form.vars.keys()]
                for e in extras:
                    form.vars[e] = rvars[e] if e in rvars.keys() \
                        else ''
                if 'id' in form.vars.keys() and form.vars['id'] in (None, ''):
                    del(form.vars['id'])
            else:
                pass

            if form.process(formname=formname).accepted:
                flash = 'The changes were recorded successfully.'

                # either redirect or refresh the list pane
                if 'redirect' in rvars and 'True' == rvars['redirect']:
                    redirect(URL(rvars['redirect_c'], rvars['redirect_a']))
                else:
                    the_url = URL('plugin_listandedit', 'itemlist.load',
                                  args=[tablename], vars={'orderby': orderby,
                                                          'restrictor': restrictor,
                                                          'collation': collation})
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
