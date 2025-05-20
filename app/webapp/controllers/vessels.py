from webapp.schemas.vessels import VesselListRequest
from django.db import transaction
from webapp.models.sailboat import Sailboat, Make
from webapp.models.vessel import Vessel
from webapp.schemas.vessels import VesselCreateRequest


def get_vessels(request: VesselListRequest):
    """finds <page_size> vessels, starting from <page>, that match the filters"""
    raise NotImplementedError("Not implemented yet")

@transaction.atomic
def create_vessel(request: VesselCreateRequest) -> int:
    """creates a new vessel, returns the id of the vessel
    (so the view layer can create a template or a data object)
    """
    if not (sailboat := Sailboat.objects.filter(id=request.sailboat).first()):
        make = Make.get_or_create_moderated(name=request.make.lower(),
                                            user=request.user)
        sailboat = Sailboat.get_or_create_moderated(make=make,
                                                    name=request.sailboat_name.lower(),
                                                    year_built=request.year_built,
                                                    user=request.user)
    vessel = Vessel.objects.create(
        sailboat=sailboat,
        hull_identification_number=request.hull_identification_number,
        name=request.name,
        year_built=request.year_built,
    )

    # handle images and attributes
    for image in request.images:
        vessel.add_image(image)

    for attribute in request.attributes:
        vessel.create_or_update_attribute(attribute)

    for attribute_assignment in request.attributes:
        vessel.create_or_update_attribute(attribute_assignment)

    vessel.save()
    return vessel.id