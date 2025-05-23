from django.shortcuts import render


def terms_of_service(request):
    """Display the Terms of Service page."""
    return render(request, "webapp/terms_of_service.html")
