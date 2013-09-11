# Module holding widget functions and classes for plugin_widgets
from gluon import A, URL, SQLFORM, DIV


class POPOVER():
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
    TODO: Put this function in a general plugin_widgets.js function
    '''

    def __init__(self):
        ''''''
        pass

    def widget(self, linktext, content, classnames=None,
               trigger='click', placement='bottom', **kwargs):
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
