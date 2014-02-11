from gluon import current, URL, LOAD
response = current.response

# CSS imported directly into framework.less
#response.files.append(URL('static',
            #'plugin_listandedit/plugin_listandedit.css'))


def plugin_listandedit():
    '''
    Public interface method to call in views in order to embed the
    plugin_listandedit widget.
    '''

    response.files.append(URL('static',
                              'plugin_listandedit/plugin_listandedit.js'))
    return LOAD('plugin_listandedit', 'widget.load', ajax=True)
