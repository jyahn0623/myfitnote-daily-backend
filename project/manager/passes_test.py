
def check_user_has_companymanager_attribute(user):
    # if user is anonymous user, return False
    if user.is_anonymous:
        return False
    # Check if user has companymanager attribute
    return hasattr(user, 'companymanager')
    
