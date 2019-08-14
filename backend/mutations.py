import six

from graphene import relay
from graphene.types import InputField, String, AbstractType
from graphene.utils.props import props

from .fields import Errors, Viewer


class Mutation(AbstractType, relay.ClientIDMutation):
    viewer = Viewer()
    errors = Errors()

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
       cls, output=None, input_fields=None, arguments=None, name=None, **options
    ):
       super(Mutation, cls).__init_subclass_with_meta__(
           output=output, input_fields=input_fields, arguments=arguments, name=name, **options
       )
       cls._meta.arguments['input']._meta.fields['revision_message'] = InputField(String, required=False)

    @classmethod
    def mutate(cls, root, info, input):
        info.context.revisionMessage = input.get('revision_message') or input.get('revisionMessage')
        return super().mutate(root, info, input)
