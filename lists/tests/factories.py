import factory

from lists.models import CollectionItem, WishItem

class CollectionItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CollectionItem

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj


class WishItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WishItem

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj


