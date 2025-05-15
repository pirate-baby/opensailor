from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def admin_or_moderator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_admin or request.user.is_moderator):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect('sailboats_index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view