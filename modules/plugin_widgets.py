# Module holding widget functions and classes for plugin_widgets
from gluon import A, URL


class JQMODAL():
    '''
    Provides a reusable link to open a modal window using the jquery-ui dialog.
    '''
    def __init__(self):
        pass

    def widget(self, label, target, cname, fname, settings=None, linkargs=None):
        '''
        Returns the actual link to activate the jq-ui modal dialog.
        '''
        linkid = 'plugin_widgets_jqmodal_{}'.format(fname)
        modal_link = A(label,
                    _id=linkid,
                    _class='plugin_widgets_jqmodal',
                    _href=URL(cname, fname, args=[linkargs]),
                    cid=target)
        return modal_link
