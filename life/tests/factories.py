import factory

from life.models import LifeNode, RANK_SPECIES


class LifeNodeFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: "Life Node %d" % n)
    rank = RANK_SPECIES

    class Meta:
        model = LifeNode

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj

