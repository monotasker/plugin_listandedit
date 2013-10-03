""" Module holding widget functions and classes for plugin_widgets """
from gluon import A, URL, SQLFORM, DIV, SPAN, current, UL, LI


def TABS(tablist):
    '''
    Provides a bootstrap tabs widget.
    label, did, content, visible=False
    '''
    tabs = DIV(_class='tabbable')
    tabnav = UL(_class='nav nav-tabs')
    tabcontent = DIV(_class='tab-content')
    for tab in tablist:
        label = tab[0]
        div_id = tab[1]
        content = tab[2]
        class_string = tab[3] if len(tab) > 3 else ' '

        # use dict because of hyphen in data-toggle
        a_args = {'_href': '#{}'.format(div_id),
                  '_data-toggle': 'tab'}
        tabnav.append(LI(A(label, **a_args)))
        wrapper = DIV(_id=div_id, _class="tab-pane {}".format(class_string))
        wrapper.append(content)
        tabcontent.append(wrapper)

    tabs.append(tabnav)
    tabs.append(tabcontent)

    return tabs


class POPOVER(object):
    '''
    Provides a bootstrap popover widget which allows html content.

    If a LOAD helper is passed as the content this popover can also be
    populated using web2py's ajax function and a separate view.


    The parent view must include this jquery function:

        $('.popover-trigger').each(function() {
            var $this = $(this);
            $this.popover({
                html: true,
                content: $this.find('.popover-content').html()
            });
        });
    TODO: Put this function in a general plugin_widgets.js file
    '''

    def __init__(self):
        ''''''
        pass

    def widget(self, linktext, content, classnames=None,
               trigger='click', placement='bottom', id=None, **kwargs):
        '''
        Returns the actual popover widget.

        In addition to the link text and
        popup content, any of the bootstrap popover properties may be set by
        passing a keyword-argument whose name is the property in question.

        The inline style display:none is necessary to hide the popover content
        initially.
        '''
        myid = linktext if not id else id
        classes = "popover-trigger {}".format(classnames)
        myargs = {'_data-trigger': trigger,
                  '_data-placement': placement,
                  '_data-toggle': 'popover'}
        if kwargs:
            newargs = {'_data-{}'.format(k): v for k, v in kwargs.iteritems()}
            myargs.update(newargs)
        popover = DIV(linktext, _id=myid, _class=classes, **myargs)
        popover.append(DIV(content, _class="popover-content",
                           _style="display: none"))
        return popover


class JQMODAL():
    '''
    Provides a reusable link to open a modal window using the jquery-ui dialog.
    Implement via model file or in form definition function like this:

    db.plugin_slider_slides.content.widget = lambda field, value: \
                                        JQMODAL(field, value).textarea('image',
                                                        'image_picker',
                                                        'plugin_widgets',
                                                        'image_picker.load')
    '''
    def __init__(self, field, value):
        '''
        Instantiate a JQMODAL object which can then generate a form field
        with an added button to open a related modal dialog.
        '''
        self.field = field
        self.value = value

    def textarea(self, label, target, cname, fname, linkargs=None):
        '''
        Returns the actual link to activate the jq-ui modal dialog.
        '''

        old_widget = SQLFORM.widgets.text.widget(self.field, self.value)
        # TODO finish this logic and change return object
        linkid = 'plugin_widgets_jqmodal_{}'.format(fname)
        modal_link = A(label,
                    _id=linkid,
                    _class='plugin_widgets_jqmodal',
                    _href=URL(cname, fname, args=[linkargs]),
                    cid=target)
        return old_widget, modal_link


def ICONLINK(title, text, icon):
    linktitle = '{}_icon'.format(title)
    link_classes = '{} icon-only icon-{}'.format(linktitle, icon)
    link = A(SPAN(text, _class='accessible'),
             _href='#',
             _class=link_classes,
             _id=linktitle)
    return link


def TOOLTIP(title, text, content, icon=None):
    '''
    Build and return a tooltip widget with the supplied content.
    '''
    # build widget wrapper
    wrapper_title = '{}_wrapper'.format(title)
    wrapper_classes = '{} tip_wrapper'.format(wrapper_title)
    tip_wrapper = DIV(_class=wrapper_classes, _id=wrapper_title)

    # add tip trigger link
    if icon:
        tip_wrapper.append(ICONLINK(title, text, icon))
    else:
        trigger_title = '{}_trigger'.format(title)
        trigger_classes = '{} trigger'.format(trigger_title)
        tip_wrapper.append(A(text, _classes=trigger_classes, _id=trigger_title))

    # add tip content
    tip_classes = '{} tip'.format(title)
    tip_wrapper.append(DIV(content, _class=tip_classes, _id=title))

    return tip_wrapper


def ROLE(content, role=None):
    '''
    Wrap some web2py helpers or html content in a condition so that it is only
    returned if the current user is logged in.
    '''
    auth = current.auth
    if role is None:
        role = 'administrators'

    if auth.has_membership(role):
        return content
    else:
        return u'\u200b'
