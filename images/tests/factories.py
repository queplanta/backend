import factory

from images.models import Image


class ImageFactory(factory.django.DjangoModelFactory):
    description = factory.Sequence(lambda n: "Image Description %d" % n)

    class Meta:
        model = Image

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj