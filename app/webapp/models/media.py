import uuid
import os
from io import BytesIO
from django.db import models
from PIL import Image as PilImage
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

MEDIA_TYPE_CHOICES = [
    ("image", "Image"),
    ("video", "Video"),
    ("audio", "Audio"),
    ("document", "Document"),
]


class Media(models.Model):
    """storing file-like media objects"""

    file = models.FileField(null=False, blank=False)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)

    def save(self, *args, **kwargs):
        if not self.id:
            # Validate file exists
            if not self.file:
                raise ValueError("File is required")

            # Get file extension from the filename
            file_extension = os.path.splitext(self.file.name)[1].lower()

            if file_extension in [".jpg", ".jpeg", ".png"]:
                filename = "image-" + str(uuid.uuid4()) + file_extension
                self.file.name = filename
                self.media_type = "image"  # Set media_type for images
            else:
                # error
                raise ValueError("Invalid file type")

            # Only resize if we have a valid file
            resized_file = self.resize_uploaded_image(self.file, 1024, 1024)
            if resized_file:
                self.file = resized_file

        super().save(*args, **kwargs)

    @classmethod
    def resize_uploaded_image(cls, image, max_width, max_height):
        if not image:
            return None

        size = (max_width, max_height)

        # Uploaded file is in memory
        if isinstance(image, InMemoryUploadedFile):
            try:
                memory_image = BytesIO(image.read())
                pil_image = PilImage.open(memory_image)
                img_format = os.path.splitext(image.name)[1][1:].upper()
                img_format = "JPEG" if img_format == "JPG" else img_format

                if pil_image.width > max_width or pil_image.height > max_height:
                    pil_image.thumbnail(size)

                new_image = BytesIO()
                pil_image.save(new_image, format=img_format)

                new_image = ContentFile(new_image.getvalue())
                return InMemoryUploadedFile(
                    new_image, None, image.name, image.content_type, None, None
                )
            except Exception:
                # If there's any error, return the original image
                image.seek(0)
                return image

        # Uploaded file is in disk
        elif isinstance(image, TemporaryUploadedFile):
            try:
                path = image.temporary_file_path()
                pil_image = PilImage.open(path)

                if pil_image.width > max_width or pil_image.height > max_height:
                    pil_image.thumbnail(size)
                    pil_image.save(path)
                    image.size = os.stat(path).st_size
                return image
            except Exception:
                # If there's any error, return the original image
                return image

        # Return the original image for any other case
        return image

    @property
    def url(self):
        if not self.file:
            return ""
        return self.file.url.replace(
            settings.AWS_S3_ENDPOINT_URL, settings.AWS_S3_CLIENT_ENDPOINT_URL
        )
