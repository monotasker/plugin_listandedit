""" Module holding widget functions and classes for plugin_widgets """
from gluon import A, URL, SQLFORM, DIV, SPAN, current, UL, LI, BUTTON, H3, CAT


def TABS(tablist):
    '''
    Returns a bootstrap 2.3.2 tabs widget in a web2py DIV() helper object.

    This function expects a single argument, a list of tuples. Each tuple
    represents a single tab in the tab set. The items in each tuple should
    contain:
        [0]     (required) the tab label text (str)
        [1]     (required) the id to be assigned to the tab content div (str)
        [2]     (required) the content to be revealed by the tab (str or
                            web2py html helper object). If a LOAD helper is
                            the value provided here the content of the tab
                            will be loaded via ajax at page load.
        [3]     (optional) extra classes to be assigned to the content
                            div (str). If a tab is to be selected by default
                            when the page loads, this tab should be passed a
                            string in this position that includes the class
                            'active'.
    There is currently no support for pill or pull-down styles of tabs.
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
    Returns a bootstrap 2.3.2 popover widget which allows html content.

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


def MODAL(triggertext, headertext, body,
          footer=None, modal_classes='', trigger_classes=None, id='mymodal',
          trigger_type='link', attributes=None):
    '''
    Returns a bootstrap 2.3.2 modal widget wrapped in a web2py CAT() helper.

    The following positional arguments are required:
        [0] triggertext     (str) The text for the link to trigger the modal.
        [1] headertext      (str or 0) The text for the modal header. If the
                            value is 0, no header will be included.
        [2] body            (str or helper obj) The content to be displayed in
                            the modal body. If this is a LOAD helper the body
                            content will be loaded via ajax.

    The following named arguments are optional:
        :footer              (str, helper obj, or 0) The content to be displayed in
                            the modal footer. If this argument is not provided,
                            the default footer is a simple "Close" button. If
                            the value is the integer 0, no footer will be
                            included at all.
        :modal_classes       (str) A string including the extra classes to be
                            assigned to the modal div.
        :trigger_classes     (str) A string including the extra classes to be
                            assigned to the button/link triggering the modal.
        :id                  (str or int) The id to be assigned to the modal div.
                            defaults to 'mymodal'. If multiple modals are
                            present on a paget this value must be specified
                            (and distinct) for each. The id for the trigger
                            will always be this same string with the suffix
                            '_trigger'.
        :trigger_type        (str: 'button' | 'link') Specifies the html entity
                            to be used to trigger the modal. Defaults to 'link'
                            which returns an A() helper.
        :attributes          (dict) The names and values of any attributes to
                            be assigned to the modal div. These can include
                            data-attributes for setting additional options (as
                            per the bootstrap 2.3.2 api).

    The close button in the default footer requires no extra javascript (beyond
    the Bootstrap modal plugin).
    '''
    # create trigger
    t_classes = trigger_classes if trigger_classes else 'btn'
    t_args = {'_data-toggle': 'modal',
              '_data-target': '#{}'.format(id),
              '_id': '{}_trigger'.format(id),
              '_class': t_classes}
    if attributes:
        t_args.update(attributes)
    if trigger_type == 'link':
        trigger = A(triggertext, **t_args)
    else:
        trigger = BUTTON(triggertext, **t_args)

    # create wrapper div for modal
    modal_attrs = {'_tabindex': '-1',
                   '_role': 'dialog',
                   '_aria-labelledby': 'myModalLabel',
                   '_aria-hidden': 'true'}
    modal = DIV(_class="modal hide fade {}".format(modal_classes),
                _id=id, **modal_attrs)

    # add header
    if headertext != 0:
        m_head = DIV(H3(headertext), _class="modal-header")
        modal.append(m_head)
    else:
        pass

    # add body content
    modal.append(DIV(body, _class='modal-body {}'.format(modal_classes)))
    # add footer
    if footer and footer != 0:
        modal.append(DIV(footer, _class='modal-footer'))
    elif not footer:
        attrs = {'_type': 'button',
                 '_class': 'close',
                 '_data-dismiss': "modal",
                 '_aria-hidden': "true"}
        modal.append(DIV(BUTTON('Close', **attrs), _class='modal-footer'))
    else:
        pass

    return CAT(trigger, modal)


def ACCORDION(panels, id='my_accordion'):
    '''
    [0]     pid
    [1]     panel link text
    [2]     panel content
    [3]     body classes (string); 'in' marks default panel
    '''
    acc = DIV(_class='accordion', _id=id)
    for panel in panels:
        pid = panel[0]
        linktext = panel[1]
        content = panel[2]
        bclasses = panel[3] if (len(panel) > 0) else ''
        linkattrs = {'_class': "accordion-toggle {}-toggle".format(pid),
                     '_data-toggle': "collapse",
                     '_data-parent': "#{}".format(id),
                     '_href': "#{}".format(pid)}
        headattrs = {'_class': "accordion-heading"}
        bodyattrs = {'_class': 'accordion-body collapse {}'.format(bclasses)}
        innerattrs = {'_class': 'accordion-inner'}
        groupattrs = {'_class': "accordion-group"}
        p = DIV(DIV(A(linktext, **linkattrs), **headattrs),
                DIV(DIV(content, **bodyattrs), **innerattrs),
                **groupattrs)

        acc.append(p)
    return acc


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
