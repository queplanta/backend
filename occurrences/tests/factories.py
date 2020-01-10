import factory

from django.contrib.gis.geos import Point

from occurrences.models import Occurrence

def document_factory(fac):
    class DocumentFactory(fac):
        @classmethod
        def _create(cls, model_class, *args, **kwargs):
            obj = fac._create(model_class, *args, **kwargs)
            return obj.document
    return DocumentFactory


class DocumentSubFactory(factory.SubFactory):
    def generate(self, step, params):
        obj = super().generate(step, params)
        return obj.document


class OccurrenceFactory(factory.django.DjangoModelFactory):
    #  title = factory.Sequence(lambda n: "Life Node %d" % n)
    identity = DocumentSubFactory('life.tests.factories.LifeNodeFactory')
    author = DocumentSubFactory('accounts.tests.factories.UserFactory')
    location = Point(-19.912338, -43.9331527)

    class Meta:
        model = Occurrence

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj


