from django.shortcuts import render
from django.core.paginator import Paginator
from webapp.models.sailboat import Sailboat
from webapp.models.attribute import Attribute

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
    sailboats = Sailboat.get_filtered_queryset(filters, order_by)

    # Paginate results
    paginator = Paginator(sailboats, 12)  # Show 12 sailboats per page
    page_obj = paginator.get_page(page_number)

    # Get all makes and designers for filter dropdowns
    makes = Sailboat.objects.values_list('make__name', flat=True).distinct().order_by('make__name')
    designers = Sailboat.objects.values_list('designers__name', flat=True).distinct().order_by('designers__name')

    # Get all attributes and their values for multi-select filters
    attributes = {}
    for attr in Attribute.objects.all():
        # Get all unique values for this attribute across all sailboats
        values = Sailboat.objects.filter(
            attribute_values__attribute=attr
        ).values_list(
            'attribute_values__values', flat=True
        ).distinct()

        # Flatten the list of lists and get unique values
        unique_values = sorted(set(
            value for sublist in values if sublist
            for value in sublist
        ))

        if unique_values:  # Only include attributes that have values
            attributes[attr.name] = unique_values

    context = {
        'page_obj': page_obj,
        'makes': makes,
        'designers': designers,
        'attributes': attributes,
        'current_filters': request.GET,
        'order_by': order_by,
    }

    return render(request, 'webapp/sailboats/index.html', context)