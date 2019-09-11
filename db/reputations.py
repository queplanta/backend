def get_perms_by_reputation(obj, user):
    perms = []
    has_obj_perms = user.is_authenticated and (user.is_superuser or \
                    user.document == obj.document.revision_created.author)
    is_user_rep_gte = lambda user, rep: user.is_authenticated and user.reputation >= rep

    if has_obj_perms:
        perms.append('edit')
        perms.append('delete')

    obj_class_name = obj.__class__.__name__

    if obj_class_name == 'Occurrence':
        if is_user_rep_gte(user, 10) or has_obj_perms:
            perms.append('identify')

    return perms
