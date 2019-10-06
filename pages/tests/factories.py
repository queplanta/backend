import factory

from pages.models import Page


class PageFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Page Title %d" % n)
    url = factory.Sequence(lambda n: "page-slug-%d" % n)

    class Meta:
        model = Page

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj