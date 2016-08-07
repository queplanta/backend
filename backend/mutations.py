from graphene import relay

from .fields import Errors, Viewer


class Mutation(relay.ClientIDMutation):
    viewer = Viewer()
    errors = Errors()

    class Meta:
        abstract = True
