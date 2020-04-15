import factory

from usages.models import Usage


class UsageFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Usage Title %d" % n)
    body = factory.Sequence(lambda n: "Usage Body %d" % n)

    class Meta:
        model = Usage

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj
