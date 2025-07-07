from pytest import mark as m
from django.template import Context, Template
from django.test import TestCase
from webapp.models import Media
from django.core.files.uploadedfile import SimpleUploadedFile


@m.describe("Responsive Images Template Tags")
class TestResponsiveImages(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a mock image file
        image_file = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        self.media = Media.objects.create(
            file=image_file,
            media_type="image"
        )

    @m.it("Should render responsive_image tag with default values")
    def test_responsive_image_default(self):
        template = Template('{% load responsive_images %}{% responsive_image image %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        # Check that basic img tag is rendered
        assert '<img' in rendered
        assert f'src="{self.media.url}"' in rendered
        assert 'loading="lazy"' in rendered
        assert 'sizes="100vw"' in rendered

    @m.it("Should render responsive_image tag with custom alt text")
    def test_responsive_image_custom_alt(self):
        template = Template('{% load responsive_images %}{% responsive_image image alt_text="Custom alt text" %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'alt="Custom alt text"' in rendered

    @m.it("Should render responsive_image tag with custom CSS classes")
    def test_responsive_image_custom_classes(self):
        template = Template('{% load responsive_images %}{% responsive_image image css_classes="custom-class" %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'class="w-full h-full object-cover custom-class"' in rendered

    @m.it("Should render responsive_image tag without lazy loading")
    def test_responsive_image_no_lazy(self):
        template = Template('{% load responsive_images %}{% responsive_image image lazy=False %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'loading="lazy"' not in rendered

    @m.it("Should render responsive_image tag with custom sizes")
    def test_responsive_image_custom_sizes(self):
        template = Template('{% load responsive_images %}{% responsive_image image sizes="320px" %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'sizes="320px"' in rendered

    @m.it("Should render card_image tag with predefined sizes")
    def test_card_image(self):
        template = Template('{% load responsive_images %}{% card_image image alt_text="Card image" %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'alt="Card image"' in rendered
        assert 'sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"' in rendered

    @m.it("Should render detail_image tag with predefined sizes")
    def test_detail_image(self):
        template = Template('{% load responsive_images %}{% detail_image image alt_text="Detail image" %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'alt="Detail image"' in rendered
        assert 'sizes="(max-width: 1024px) 100vw, 66vw"' in rendered

    @m.it("Should render thumbnail_image tag with predefined sizes")
    def test_thumbnail_image(self):
        template = Template('{% load responsive_images %}{% thumbnail_image image alt_text="Thumbnail image" %}')
        context = Context({'image': self.media})
        rendered = template.render(context)
        
        assert 'alt="Thumbnail image"' in rendered
        assert 'sizes="120px"' in rendered