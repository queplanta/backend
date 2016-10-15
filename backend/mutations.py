import six

from graphene import relay
from graphene.types import String, AbstractType
from graphene.utils.props import props

from .fields import Errors, Viewer


class MutationRevisionMessage(AbstractType):
    revisionMessage = String(required=False)


class MutationMeta(relay.mutation.ClientIDMutationMeta):
    def __new__(cls, name, bases, attrs):
        input_class = attrs.pop('Input', None)
        if input_class:
            input_attrs = props(input_class)
            attrs['Input'] = type('Input',
                                  (input_class, MutationRevisionMessage),
                                  input_attrs)
            cls.Input = attrs['Input']
        return super().__new__(cls, name, bases, attrs)


class Mutation(six.with_metaclass(MutationMeta, relay.ClientIDMutation,
                                  AbstractType)):
    viewer = Viewer()
    errors = Errors()

    @classmethod
    def mutate(cls, root, args, context, info):
        input = args.get('input')
        context.revisionMessage = input.get('revisionMessage') \
            or input.get('revision_message')
        return super(Mutation, cls).mutate(root, args, context, info)
