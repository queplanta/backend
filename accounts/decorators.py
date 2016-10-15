from functools import wraps

from backend.fields import LoginRequiredError


def user_passes_test(test_func):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(cls, args, context, info):
            if test_func(context.user):
                return view_func(cls, args, context, info)
            return cls(errors=[LoginRequiredError()])
        return _wrapped_view
    return decorator


def login_required(function):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
