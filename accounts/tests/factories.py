import factory

from accounts.models import User

class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "user-%d" % n)
    email = factory.Sequence(lambda n: 'user-{0}+test@queplanta.com'.format(n))

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.save(request=None)
        return obj
