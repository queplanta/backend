import six

from graphene import relay
from graphene.core.types.argument import ArgumentsGroup
from graphene.core.types.definitions import NonNull
from graphene.core.types import String
from graphene.utils import with_context

from .fields import Errors, Viewer


class MutationRevisionMessage(relay.types.MutationInputType):
    revisionMessage = String(required=False)


class MutationMeta(relay.types.RelayMutationMeta):
    def construct_arguments(cls, items):
        new_input_type = type('{}Input'.format(
            cls._meta.type_name), (MutationRevisionMessage, ), items)
        cls.add_to_class('input_type', new_input_type)
        return ArgumentsGroup(input=NonNull(new_input_type))


class Mutation(six.with_metaclass(MutationMeta, relay.ClientIDMutation)):
    viewer = Viewer()
    errors = Errors()

    class Meta:
        abstract = True

    @classmethod
    @with_context
    def mutate(cls, instance, args, context, info):
        input = args.get('input')
        context.revisionMessage = input.get('revisionMessage') or input.get('revision_message')
        return super(Mutation, cls).mutate(instance, args, context, info)
