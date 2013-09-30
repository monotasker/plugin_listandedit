if 0:
    from gluon import current
    auth = current.auth


def ROLE(content, role=None):
    '''
    Wrap some web2py helpers or html content in a condition so that it is only
    returned if the current user is logged in.
    '''
    if role is None:
        role = 'administrators'

    if auth.has_membership(role):
        return content
    else:
        return u'\u200b'
