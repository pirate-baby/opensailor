from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from webapp.models.sailboat import Sailboat, SailboatImage
from webapp.models.attribute import Attribute
from webapp.models.make import Make
from webapp.models.designer import Designer
from webapp.models.media import Media
from webapp.models.vessel import Vessel, VesselImage
from webapp.decorators import admin_or_moderator_required
from webapp.models.sailboat_attribute import SailboatAttribute
from webapp.models.vessel_note import VesselNote
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Get a logger for this module
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'webapp/home.html')

def sailboats_index(request):
    # Get filter parameters from request
    filters = {}
    for key in ['name', 'make', 'designer', 'year_start', 'year_end']:
        if value := request.GET.get(key):
            filters[key] = value

    # Get attribute filters
    for key, value in request.GET.items():
        if key.startswith('attr_') and value:
            # Handle multiple values for the same attribute
            if key in filters:
                if isinstance(filters[key], list):
                    filters[key].append(value)
                else:
                    filters[key] = [filters[key], value]
            else:
                filters[key] = value

    # Get ordering parameter
    order_by = request.GET.get('order_by', 'name')

    # Get page number
    page_number = request.GET.get('page', 1)

    # Get filtered queryset
    sailboats = Sailboat.objects.all() #(filters, order_by)

    # Paginate results
    paginator = Paginator(sailboats, 12)  # Show 12 sailboats per page
    page_obj = paginator.get_page(page_number)

    # Get all makes and designers for filter dropdowns
    makes = Sailboat.objects.values_list('make__name', flat=True).distinct().order_by('make__name')
    designers = Sailboat.objects.values_list('designers__name', flat=True).distinct().order_by('designers__name')

    context = {
        'page_obj': page_obj,
        'makes': makes,
        'designers': designers,
        'attributes': Attribute.objects.all(),
        'current_filters': request.GET,
        'order_by': order_by,
    }

    return render(request, 'webapp/sailboats/index.html', context)

@admin_or_moderator_required
def sailboat_create(request):
    if request.method == 'POST':
        try:
            # Get or create make
            make_name = request.POST.get('make').lower()
            make, _ = Make.objects.get_or_create(name=make_name)

            # Create sailboat
            sailboat = Sailboat.objects.create(
                name=request.POST.get('name').lower(),
                make=make,
                manufactured_start_year=request.POST.get('manufactured_start_year'),
                manufactured_end_year=request.POST.get('manufactured_end_year')
            )

            # Handle designers
            designer_names = [name.strip().lower() for name in request.POST.get('designers', '').split(',')]
            for designer_name in designer_names:
                if designer_name:
                    designer, _ = Designer.objects.get_or_create(name=designer_name)
                    sailboat.designers.add(designer)

            # Handle attributes
            all_attributes = Attribute.objects.all()

            # Process each attribute from the form
            for attr in all_attributes:
                # Check if the attribute is in the form
                if not attr.is_in_form_data(request.POST):
                    continue

                # Get values for this attribute
                values = attr.get_values_from_form_data(request.POST)

                # Only create the attribute if there are values
                if values:
                    SailboatAttribute.objects.create(
                        sailboat=sailboat,
                        attribute=attr,
                        values=values
                    )

            # Handle images
            images = request.FILES.getlist('images')
            for index, image in enumerate(images):
                media = Media.objects.create(file=image)
                # Create the through model instance instead of using add()
                SailboatImage.objects.create(sailboat=sailboat, image=media, order=index)

            messages.success(request, 'Sailboat created successfully.')
            return redirect('sailboat_detail', pk=sailboat.pk)
        except Exception as e:
            messages.error(request, f'Error creating sailboat: {str(e)}')

    context = {
        'makes': Make.objects.all().order_by('name'),
        'designers': Designer.objects.all().order_by('name'),
        'attributes': Attribute.objects.all(),
    }
    return render(request, 'webapp/sailboats/create.html', context)

def sailboat_detail(request, pk):
    sailboat = get_object_or_404(Sailboat, pk=pk)

    # Load all sailboat attributes for display
    sailboat_attributes = sailboat.attribute_values.select_related('attribute').all()

    context = {
        'sailboat': sailboat,
        'attributes': Attribute.objects.all(),
        'sailboat_attributes': sailboat_attributes,
    }
    return render(request, 'webapp/sailboats/detail.html', context)

@admin_or_moderator_required
def sailboat_update(request, pk):
    sailboat = get_object_or_404(Sailboat, pk=pk)

    if request.method == 'POST':
        try:
            # Update make
            make_name = request.POST.get('make').lower()
            make, _ = Make.objects.get_or_create(name=make_name)

            # Update sailboat
            sailboat.name = request.POST.get('name').lower()
            sailboat.make = make
            sailboat.manufactured_start_year = request.POST.get('manufactured_start_year')
            sailboat.manufactured_end_year = request.POST.get('manufactured_end_year')
            sailboat.save()

            # Update designers
            sailboat.designers.clear()
            designer_names = [name.strip().lower() for name in request.POST.get('designers', '').split(',')]
            for designer_name in designer_names:
                if designer_name:
                    designer, _ = Designer.objects.get_or_create(name=designer_name)
                    sailboat.designers.add(designer)

            # Log the start of attribute updates
            logger.info(f"Starting attribute updates for sailboat {sailboat.id} ({sailboat.name})")

            all_attributes = Attribute.objects.all()
            for attr in all_attributes:
                # Check if the attribute is in the form
                if not attr.is_in_form_data(request.POST):
                    logger.info(f"Attribute {attr.id} ({attr.snake_case_name}) not in form, skipping")
                    continue

                # Get values for this attribute
                values = attr.get_values_from_form_data(request.POST)

                if not values:
                    deleted = sailboat.attribute_values.filter(attribute=attr).delete()
                    logger.info(f"Deleted attribute {attr.id} ({attr.snake_case_name}) for sailboat {sailboat.id}: {deleted}")
                    continue

                _, created = SailboatAttribute.objects.update_or_create(
                    sailboat=sailboat,
                    attribute=attr,
                    defaults={'values': values}
                )
                logger.info(f"{'Created' if created else 'Updated'} new attribute {attr.id} ({attr.snake_case_name}) for sailboat {sailboat.id} with values: {values}")

            logger.info(f"Completed attribute updates for sailboat {sailboat.id}")

            # Handle new images
            images = request.FILES.getlist('images')
            for index, image in enumerate(images):
                media = Media.objects.create(file=image)
                SailboatImage.objects.create(sailboat=sailboat, image=media, order=index)

            messages.success(request, 'Sailboat updated successfully.')
            return redirect('sailboat_detail', pk=sailboat.pk)
        except Exception as e:
            logger.error(f"Error in sailboat_update for sailboat {pk}: {str(e)}")
            messages.error(request, f'Error updating sailboat: {str(e)}')

    # Get the sailboat's attributes for the form
    sailboat_attributes = sailboat.attribute_values.select_related('attribute').all()

    context = {
        'sailboat': sailboat,
        'makes': Make.objects.all().order_by('name'),
        'designers': Designer.objects.all().order_by('name'),
        'attributes': Attribute.objects.all(),
        'sailboat_attributes': sailboat_attributes,
    }
    return render(request, 'webapp/sailboats/update.html', context)

@admin_or_moderator_required
def sailboat_delete(request, pk):
    sailboat = get_object_or_404(Sailboat, pk=pk)

    if request.method == 'POST':
        try:
            sailboat.delete()
            messages.success(request, 'Sailboat deleted successfully.')
            return redirect('sailboats_index')
        except Exception as e:
            messages.error(request, f'Error deleting sailboat: {str(e)}')

    return render(request, 'webapp/sailboats/delete.html', {'sailboat': sailboat})

def vessels_index(request):
    # Get search parameter from request
    search_query = request.GET.get('search', '')

    # Start with all vessels
    vessels = Vessel.objects.all().select_related('sailboat', 'sailboat__make')

    # Filter by search query - check both HIN and name
    if search_query:
        vessels = vessels.filter(hull_identification_number__icontains=search_query) | vessels.filter(name__icontains=search_query)

    # Get page number
    page_number = request.GET.get('page', 1)

    # Paginate results
    paginator = Paginator(vessels, 12)  # Show 12 vessels per page
    page_obj = paginator.get_page(page_number)

    # Get vessels with notes for the current user if they're authenticated
    user_vessels_with_notes = Vessel.objects.filter(
        notes__user=request.user
    ) if request.user.is_authenticated else Vessel.objects.none()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_vessels_with_notes': user_vessels_with_notes,
    }

    return render(request, 'webapp/vessels/index.html', context)

def vessel_detail(request, pk):
    vessel = get_object_or_404(Vessel, pk=pk)
    user_note = None
    if request.user.is_authenticated:
        user_note = VesselNote.objects.filter(vessel=vessel, user=request.user).first()
    context = {
        'vessel': vessel,
        'user_note': user_note,
    }
    return render(request, 'webapp/vessels/detail.html', context)

@admin_or_moderator_required
def vessel_create(request):
    if request.method == 'POST':
        try:
            # Get the sailboat
            sailboat_id = request.POST.get('sailboat')
            sailboat = get_object_or_404(Sailboat, pk=sailboat_id)

            # Create vessel
            vessel = Vessel.objects.create(
                sailboat=sailboat,
                hull_identification_number=request.POST.get('hull_identification_number').upper(),
                name=request.POST.get('name'),
                year_built=request.POST.get('year_built') or None,
            )

            # Handle images
            images = request.FILES.getlist('images')
            for index, image in enumerate(images):
                media = Media.objects.create(file=image)
                VesselImage.objects.create(vessel=vessel, image=media, order=index)

            messages.success(request, 'Vessel created successfully.')
            return redirect('vessel_detail', pk=vessel.pk)
        except Exception as e:
            messages.error(request, f'Error creating vessel: {str(e)}')

    context = {
        'sailboats': Sailboat.objects.all().order_by('make__name', 'name'),
    }
    return render(request, 'webapp/vessels/create.html', context)

@admin_or_moderator_required
def vessel_update(request, pk):
    vessel = get_object_or_404(Vessel, pk=pk)

    if request.method == 'POST':
        try:
            # Get the sailboat
            sailboat_id = request.POST.get('sailboat')
            sailboat = get_object_or_404(Sailboat, pk=sailboat_id)

            # Update vessel
            vessel.sailboat = sailboat
            for field in ['hull_identification_number', 'name', 'home_port', 'year_built']:
                setattr(vessel, field, request.POST.get(field))
            vessel.save()

            # Handle new images
            images = request.FILES.getlist('images')
            for index, image in enumerate(images):
                media = Media.objects.create(file=image)
                # Get the highest order value
                highest_order = vessel.vesselimage_set.order_by('-order').first()
                next_order = (highest_order.order + 1) if highest_order else 0
                VesselImage.objects.create(vessel=vessel, image=media, order=next_order + index)

            messages.success(request, 'Vessel updated successfully.')
            return redirect('vessel_detail', pk=vessel.pk)
        except Exception as e:
            messages.error(request, f'Error updating vessel: {str(e)}')

    context = {
        'vessel': vessel,
        'sailboats': Sailboat.objects.all().order_by('make__name', 'name'),
    }
    return render(request, 'webapp/vessels/update.html', context)

@admin_or_moderator_required
def vessel_delete(request, pk):
    vessel = get_object_or_404(Vessel, pk=pk)

    if request.method == 'POST':
        try:
            vessel.delete()
            messages.success(request, 'Vessel deleted successfully.')
            return redirect('vessels_index')
        except Exception as e:
            messages.error(request, f'Error deleting vessel: {str(e)}')

    return render(request, 'webapp/vessels/delete.html', {'vessel': vessel})

@login_required
def vessel_note_update(request, pk):
    vessel = get_object_or_404(Vessel, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        note, created = VesselNote.objects.get_or_create(
            vessel=vessel,
            user=request.user,
            defaults={'content': content}
        )
        if not created:
            note.content = content
            note.save()

        if request.headers.get('HX-Request'):
            return render(request, 'webapp/components/note_status.html', {
                'status': 'success',
                'message': 'Note saved successfully'
            })
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)