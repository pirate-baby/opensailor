from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import csv
from io import TextIOWrapper, StringIO

from webapp.models import (
    User,
    Make,
    Designer,
    Attribute,
    Sailboat,
    SailboatAttribute,
    Media,
    AttributeSection,
    Moderation,
)
from webapp.models.vessel import Vessel, VesselImage, VesselAttribute
from webapp.models.sailboat import SailboatImage


class CSVImportMixin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-csv/",
                self.import_csv,
                name=f"{self.model._meta.model_name}_import_csv",
            ),
            path(
                "download-template/",
                self.download_template,
                name=f"{self.model._meta.model_name}_download_template",
            ),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "File is not CSV type")
                return redirect("..")

            csv_file = TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.DictReader(csv_file)

            try:
                self.process_csv(reader)
                messages.success(request, "Your csv file has been imported")
            except Exception as e:
                messages.error(request, f"Error importing CSV: {str(e)}")

            return redirect("..")

        context = {
            "title": f"Import CSV - {self.model._meta.verbose_name_plural}",
            "opts": self.model._meta,
        }
        return render(request, "admin/csv_form.html", context)

    def download_template(self, request):
        # Get the first instance of the model
        instance = self.model.objects.first()

        # Create a CSV file in memory
        output = StringIO()
        writer = csv.writer(output)

        # Get the field names and values
        if instance:
            # For regular models
            field_names = [f.name for f in self.model._meta.fields if f.name != "id"]
            values = [
                getattr(instance, f.name)
                for f in self.model._meta.fields
                if f.name != "id"
            ]
        else:
            # If no instances exist, just write the headers
            field_names = [f.name for f in self.model._meta.fields if f.name != "id"]
            values = [""] * len(field_names)

        # Write the header and data
        writer.writerow(field_names)
        writer.writerow(values)

        # Create the response
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.model._meta.model_name}_template.csv"'
        )

        return response

    def process_csv(self, reader):
        raise NotImplementedError("Subclasses must implement process_csv method")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_import_csv"] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )


@admin.register(Make)
class MakeAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    def process_csv(self, reader):
        for row in reader:
            Make.objects.get_or_create(name=row["name"].lower())


@admin.register(Designer)
class DesignerAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    def process_csv(self, reader):
        for row in reader:
            Designer.objects.get_or_create(name=row["name"].lower())

@admin.register(AttributeSection)
class AttributeSectionAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("name", "icon")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Attribute)
class AttributeAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("name", "input_type", "description",)
    list_filter = ("input_type",)
    search_fields = ("name", "description")
    ordering = ("name",)

    def process_csv(self, reader):
        for row in reader:
            Attribute.objects.get_or_create(
                name=row["name"].lower(),
                defaults={
                    "description": row.get("description", ""),
                    "input_type": row.get("input_type", "string"),
                    "options": row.get("options", None),
                },
            )


class SailboatAttributeInline(admin.TabularInline):
    model = SailboatAttribute
    extra = 1


class SailboatImageInline(admin.TabularInline):
    model = SailboatImage
    extra = 1
    fields = ("image", "order")


@admin.register(Sailboat)
class SailboatAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("name", "make", "manufactured_start_year", "manufactured_end_year")
    list_filter = ("make", "designers")
    search_fields = ("name", "make__name", "designers__name")
    filter_horizontal = ("designers",)
    inlines = [SailboatAttributeInline, SailboatImageInline]
    ordering = ("make__name", "name")

    def process_csv(self, reader):
        for row in reader:
            make, _ = Make.objects.get_or_create(name=row["make"].lower())
            sailboat, created = Sailboat.objects.get_or_create(
                name=row["name"].lower(),
                make=make,
                defaults={
                    "manufactured_start_year": row.get("manufactured_start_year"),
                    "manufactured_end_year": row.get("manufactured_end_year"),
                },
            )

            # Handle designers
            if "designers" in row:
                designer_names = [
                    name.strip().lower() for name in row["designers"].split(",")
                ]
                for designer_name in designer_names:
                    designer, _ = Designer.objects.get_or_create(name=designer_name)
                    sailboat.designers.add(designer)


@admin.register(SailboatAttribute)
class SailboatAttributeAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("sailboat", "attribute", "values")
    list_filter = ("attribute",)
    search_fields = ("sailboat__name", "attribute__name")
    ordering = ("sailboat__name", "attribute__name")

    def process_csv(self, reader):
        for row in reader:
            sailboat = Sailboat.objects.get(
                name=row["sailboat_name"].lower(), make__name=row["make_name"].lower()
            )
            attribute = Attribute.objects.get(name=row["attribute_name"].lower())

            # Convert values string to list
            values = [v.strip() for v in row["values"].split(",")]

            SailboatAttribute.objects.update_or_create(
                sailboat=sailboat, attribute=attribute, defaults={"values": values}
            )


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("file", "media_type", "url")
    list_filter = ("media_type",)
    search_fields = ("file",)
    readonly_fields = ("url",)
    fields = ("file", "media_type", "url")

    def url(self, obj):
        return obj.url

    url.short_description = "URL"


class VesselImageInline(admin.TabularInline):
    model = VesselImage
    extra = 1
    fields = ("image", "order")


@admin.register(Vessel)
class VesselAdmin(CSVImportMixin, admin.ModelAdmin):
    list_display = ("name", "sailboat", "hull_identification_number", "year_built")
    list_filter = ("sailboat", "year_built")
    search_fields = ("name", "hull_identification_number", "sailboat__name")
    inlines = [VesselImageInline]
    ordering = ("sailboat__name", "name")

    def process_csv(self, reader):
        for row in reader:
            try:
                sailboat = Sailboat.objects.get(name=row["sailboat_name"].lower())

                Vessel.objects.update_or_create(
                    hull_identification_number=row["hull_identification_number"],
                    defaults={
                        "sailboat": sailboat,
                        "name": row["name"],
                        "year_built": row.get("year_built", None),
                    },
                )
            except Sailboat.DoesNotExist:
                raise Exception(
                    f"Sailboat with name '{row['sailboat_name']}' does not exist"
                )
            except KeyError as e:
                raise Exception(f"Missing required field: {str(e)}")


@admin.register(SailboatImage)
class SailboatImageAdmin(admin.ModelAdmin):
    list_display = ("sailboat", "image", "order")
    list_filter = ("sailboat",)
    search_fields = ("sailboat__name", "image__file")
    ordering = ("sailboat__name", "order")


@admin.register(Moderation)
class ModerationAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "requested_by", "state", "created_at", "moderator")
    list_filter = ("state", "content_type")
    search_fields = ("requested_by__username", "moderator__username")
    readonly_fields = ("content_type", "object_id", "data", "requested_by", "created_at", "updated_at")
    fieldsets = (
        (_("Moderation Request"), {
            "fields": ("content_type", "object_id", "data", "requested_by", "request_note")
        }),
        (_("Moderation Status"), {
            "fields": ("state", "moderator", "response_note")
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at")
        }),
    )

    def has_add_permission(self, request):
        # Moderations should only be created programmatically
        return False


@admin.register(VesselAttribute)
class VesselAttributeAdmin(admin.ModelAdmin):
    list_display = ("vessel", "attribute", "value")
    list_filter = ("attribute", "vessel")
    search_fields = ("vessel__name", "attribute__name", "value")
    ordering = ("vessel__name", "attribute__name")
