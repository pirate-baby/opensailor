from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms

from webapp.models.vessel import Vessel
from webapp.models.vessel_access_request import VesselAccessRequest
from webapp.models.user import User
from webapp.decorators import vessel_skipper_required


class VesselAccessRequestForm(forms.ModelForm):
    class Meta:
        model = VesselAccessRequest
        fields = ["requested_role", "message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Why do you need access to this vessel?",
                }
            ),
            "requested_role": forms.Select(choices=VesselAccessRequest.Role.choices),
        }


@login_required
@require_http_methods(["POST"])
def vessel_access_request(request, pk):
    """Create an access request for a vessel"""
    vessel = get_object_or_404(Vessel, pk=pk)

    # Check if user already has access
    if request.user.can_view_vessel(vessel):
        messages.info(request, "You already have access to this vessel.")
        return redirect("vessel_detail", pk=vessel.pk)

    # Check if user already has a pending request
    existing_request = VesselAccessRequest.objects.filter(
        vessel=vessel, requester=request.user, status=VesselAccessRequest.Status.PENDING
    ).first()

    if existing_request:
        messages.info(
            request, "You already have a pending access request for this vessel."
        )
        return redirect("vessel_detail", pk=vessel.pk)

    # Create new request
    requested_role = request.POST.get("requested_role", "viewer")
    message = request.POST.get("message", "")

    VesselAccessRequest.objects.create(
        vessel=vessel,
        requester=request.user,
        requested_role=requested_role,
        message=message,
    )

    # Send email notification to vessel owner
    try:
        send_mail(
            subject=f"Access Request for {vessel.name}",
            message=(
                f"{request.user.get_full_name() or request.user.username} has requested {requested_role} "
                f'access to your vessel "{vessel.name}".\n\n'
                f"Message: {message}\n\n"
                f'Review this request at: {request.build_absolute_uri(reverse("vessel_manage_roles", args=[vessel.pk]))}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vessel.created_by.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Email sending is optional

    messages.success(
        request,
        f"Access request sent! The vessel owner will be notified of your {requested_role} access request.",
    )
    return redirect("vessel_detail", pk=vessel.pk)


@vessel_skipper_required
def vessel_manage_roles(request, pk):
    """Manage roles for a vessel - only skippers can access this"""
    vessel = get_object_or_404(Vessel, pk=pk)

    # Get all access requests for this vessel
    pending_requests = VesselAccessRequest.objects.filter(
        vessel=vessel, status=VesselAccessRequest.Status.PENDING
    ).order_by("-created_at")

    # Get current users with permissions
    vessel_users = []

    # Get all users who have any permission on this specific vessel
    users_with_perms = get_users_with_perms(vessel, attach_perms=True)

    for user, perms in users_with_perms.items():
        permissions = []
        if "can_manage_vessel" in perms:
            permissions.append("Skipper")
        if "can_crew_vessel" in perms:
            permissions.append("Crew")
        if "can_view_vessel" in perms:
            permissions.append("Viewer")

        if permissions:
            vessel_users.append({"user": user, "permissions": permissions})

    context = {
        "vessel": vessel,
        "pending_requests": pending_requests,
        "vessel_users": vessel_users,
    }

    return render(request, "webapp/vessels/manage_roles.html", context)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_access_approve(request, pk, request_id):
    """Approve an access request"""
    vessel = get_object_or_404(Vessel, pk=pk)
    access_request = get_object_or_404(
        VesselAccessRequest, pk=request_id, vessel=vessel
    )

    if access_request.status != VesselAccessRequest.Status.PENDING:
        messages.error(request, "This request has already been reviewed.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    access_request.approve(request.user)
    messages.success(
        request,
        f"Approved {access_request.requested_role} access for "
        f"{access_request.requester.get_full_name() or access_request.requester.username}.",
    )

    return redirect("vessel_manage_roles", pk=vessel.pk)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_access_deny(request, pk, request_id):
    """Deny an access request"""
    vessel = get_object_or_404(Vessel, pk=pk)
    access_request = get_object_or_404(
        VesselAccessRequest, pk=request_id, vessel=vessel
    )

    if access_request.status != VesselAccessRequest.Status.PENDING:
        messages.error(request, "This request has already been reviewed.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    access_request.deny(request.user)
    messages.success(
        request,
        f"Denied {access_request.requested_role} access for "
        f"{access_request.requester.get_full_name() or access_request.requester.username}.",
    )

    return redirect("vessel_manage_roles", pk=vessel.pk)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_remove_user(request, pk, user_id):
    """Remove a user's access to a vessel"""
    vessel = get_object_or_404(Vessel, pk=pk)
    user = get_object_or_404(User, pk=user_id)

    # Don't allow removing the vessel creator
    if user == vessel.created_by:
        messages.error(request, "Cannot remove vessel creator's access.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    # Remove all permissions
    remove_perm("webapp.can_manage_vessel", user, vessel)
    remove_perm("webapp.can_crew_vessel", user, vessel)
    remove_perm("webapp.can_view_vessel", user, vessel)

    messages.success(
        request, f"Removed access for {user.get_full_name() or user.username}."
    )
    return redirect("vessel_manage_roles", pk=vessel.pk)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_add_user(request, pk):
    """Add a user to a vessel with specified permissions"""
    vessel = get_object_or_404(Vessel, pk=pk)

    email = request.POST.get("email", "").strip().lower()
    role = request.POST.get("role", "viewer")

    if not email:
        messages.error(request, "Please provide an email address.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, f"No user found with email {email}.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    # Don't add duplicate permissions for existing users
    if user.can_view_vessel(vessel):
        messages.info(
            request,
            f"{user.get_full_name() or user.username} already has access to this vessel.",
        )
        return redirect("vessel_manage_roles", pk=vessel.pk)

    # Assign permissions based on role
    if role == "viewer":
        assign_perm("webapp.can_view_vessel", user, vessel)
        role_name = "Viewer"
    elif role == "crew":
        assign_perm("webapp.can_view_vessel", user, vessel)
        assign_perm("webapp.can_crew_vessel", user, vessel)
        role_name = "Crew"
    elif role == "skipper":
        assign_perm("webapp.can_view_vessel", user, vessel)
        assign_perm("webapp.can_crew_vessel", user, vessel)
        assign_perm("webapp.can_manage_vessel", user, vessel)
        role_name = "Skipper"
    else:
        messages.error(request, "Invalid role specified.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    messages.success(
        request, f"Added {user.get_full_name() or user.username} as {role_name}."
    )
    return redirect("vessel_manage_roles", pk=vessel.pk)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_change_user_role(request, pk, user_id):
    """Change a user's role on a vessel"""
    vessel = get_object_or_404(Vessel, pk=pk)
    user = get_object_or_404(User, pk=user_id)

    # Don't allow changing the vessel creator's permissions
    if user == vessel.created_by:
        messages.error(request, "Cannot change vessel creator's permissions.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    new_role = request.POST.get("role")

    # Remove all existing permissions first
    remove_perm("webapp.can_manage_vessel", user, vessel)
    remove_perm("webapp.can_crew_vessel", user, vessel)
    remove_perm("webapp.can_view_vessel", user, vessel)

    # Assign new permissions based on role
    if new_role == "viewer":
        assign_perm("webapp.can_view_vessel", user, vessel)
        role_name = "Viewer"
    elif new_role == "crew":
        assign_perm("webapp.can_view_vessel", user, vessel)
        assign_perm("webapp.can_crew_vessel", user, vessel)
        role_name = "Crew"
    elif new_role == "skipper":
        assign_perm("webapp.can_view_vessel", user, vessel)
        assign_perm("webapp.can_crew_vessel", user, vessel)
        assign_perm("webapp.can_manage_vessel", user, vessel)
        role_name = "Skipper"
    else:
        messages.error(request, "Invalid role specified.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    messages.success(
        request,
        f"Changed {user.get_full_name() or user.username}'s role to {role_name}.",
    )
    return redirect("vessel_manage_roles", pk=vessel.pk)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_revoke_permission(request, pk, user_id):
    """Revoke a specific permission from a user"""
    vessel = get_object_or_404(Vessel, pk=pk)
    user = get_object_or_404(User, pk=user_id)

    # Don't allow revoking the vessel creator's permissions
    if user == vessel.created_by:
        messages.error(request, "Cannot revoke vessel creator's permissions.")
        return redirect("vessel_manage_roles", pk=vessel.pk)

    permission = request.POST.get("permission")

    if permission == "can_manage_vessel":
        remove_perm("webapp.can_manage_vessel", user, vessel)
        messages.success(
            request,
            f"Revoked skipper permissions from {user.get_full_name() or user.username}.",
        )
    elif permission == "can_crew_vessel":
        remove_perm("webapp.can_crew_vessel", user, vessel)
        messages.success(
            request,
            f"Revoked crew permissions from {user.get_full_name() or user.username}.",
        )
    elif permission == "can_view_vessel":
        remove_perm("webapp.can_view_vessel", user, vessel)
        messages.success(
            request,
            f"Revoked view permissions from {user.get_full_name() or user.username}.",
        )
    else:
        messages.error(request, "Invalid permission specified.")

    return redirect("vessel_manage_roles", pk=vessel.pk)


@vessel_skipper_required
@require_http_methods(["POST", "GET"])
def vessel_confirm_delete(request, pk):
    """Confirm and delete a vessel with additional safety checks"""
    vessel = get_object_or_404(Vessel, pk=pk)

    # Only vessel creator can delete (even other skippers cannot)
    if request.user != vessel.created_by:
        messages.error(request, "Only the vessel creator can delete this vessel.")
        return redirect("vessel_detail", pk=vessel.pk)

    if request.method == "POST":
        # Additional safety check - require vessel name confirmation
        confirm_name = request.POST.get("confirm_name", "").strip()
        if confirm_name != vessel.name:
            messages.error(
                request, "Vessel name confirmation does not match. Deletion cancelled."
            )
            return redirect("vessel_confirm_delete", pk=vessel.pk)

        vessel_name = vessel.name
        try:
            vessel.delete()
            messages.success(
                request, f"Vessel '{vessel_name}' has been permanently deleted."
            )
            return redirect("vessels_index")
        except Exception as e:
            messages.error(request, f"Error deleting vessel: {str(e)}")
            return redirect("vessel_detail", pk=vessel.pk)

    # GET request - show confirmation page
    context = {
        "vessel": vessel,
        "user_count": len(get_users_with_perms(vessel)),
        "notes_count": vessel.vesselnote_set.count(),
    }
    return render(request, "webapp/vessels/confirm_delete.html", context)


@vessel_skipper_required
@require_http_methods(["POST"])
def vessel_toggle_privacy(request, pk):
    """Toggle vessel privacy (public/private)"""
    vessel = get_object_or_404(Vessel, pk=pk)

    vessel.is_public = not vessel.is_public
    vessel.save()

    status = "public" if vessel.is_public else "private"
    messages.success(request, f"Vessel is now {status}.")

    return redirect("vessel_detail", pk=vessel.pk)
