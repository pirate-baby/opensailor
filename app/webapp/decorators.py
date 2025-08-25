from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from webapp.models.vessel import Vessel


def admin_or_moderator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (
            request.user.is_admin or request.user.is_moderator
        ):
            messages.error(request, "You don't have permission to perform this action.")
            return redirect("sailboats_index")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def vessel_permission_required(permission):
    """
    Decorator that checks if user has specified permission on vessel.
    Expects vessel_id in URL kwargs or pk.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to access this vessel.")
                return redirect("account_login")
            
            # Get vessel ID from URL kwargs
            vessel_id = kwargs.get("vessel_id") or kwargs.get("pk")
            if not vessel_id:
                messages.error(request, "Vessel not found.")
                return redirect("vessels_index")
            
            vessel = get_object_or_404(Vessel, pk=vessel_id)
            
            # Check permission
            if not request.user.has_perm(permission, vessel):
                messages.error(request, "You don't have permission to perform this action on this vessel.")
                return redirect("vessel_detail", pk=vessel.pk)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def vessel_skipper_required(view_func):
    """Decorator that requires skipper permissions on vessel"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to manage this vessel.")
            return redirect("account_login")
        
        vessel_id = kwargs.get("vessel_id") or kwargs.get("pk")
        if not vessel_id:
            messages.error(request, "Vessel not found.")
            return redirect("vessels_index")
        
        vessel = get_object_or_404(Vessel, pk=vessel_id)
        
        if not request.user.can_manage_vessel(vessel):
            messages.error(request, "Only vessel skippers can perform this action.")
            return redirect("vessel_detail", pk=vessel.pk)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def vessel_crew_or_skipper_required(view_func):
    """Decorator that requires crew or skipper permissions on vessel"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to add logs to this vessel.")
            return redirect("account_login")
        
        vessel_id = kwargs.get("vessel_id") or kwargs.get("pk")
        if not vessel_id:
            messages.error(request, "Vessel not found.")
            return redirect("vessels_index")
        
        vessel = get_object_or_404(Vessel, pk=vessel_id)
        
        if not request.user.can_crew_vessel(vessel):
            messages.error(request, "Only vessel crew and skippers can add logs.")
            return redirect("vessel_detail", pk=vessel.pk)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def vessel_viewer_required(view_func):
    """Decorator that requires any permission to view vessel details"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to view this private vessel.")
            return redirect("account_login")
        
        vessel_id = kwargs.get("vessel_id") or kwargs.get("pk")
        if not vessel_id:
            messages.error(request, "Vessel not found.")
            return redirect("vessels_index")
        
        vessel = get_object_or_404(Vessel, pk=vessel_id)
        
        if not request.user.can_view_vessel(vessel):
            messages.error(request, "This vessel is private and you don't have permission to view it.")
            return redirect("vessels_index")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
