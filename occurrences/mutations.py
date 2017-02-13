import graphene
from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django import forms
from multiupload.fields import MultiImageField

from accounts.decorators import login_required
from backend.mutations import Mutation
from db.models_graphql import Document
from utils.forms import form_erros
from images.models import Image as ImageModel
from .models_graphql import Occurrence, SuggestionID


class OccurrenceCreateForm(forms.Form):
    images = MultiImageField(min_num=1)


class OccurrenceCreate(Mutation):
    class Input:
        when = graphene.String(required=False)
        where = graphene.String(required=False)
        notes = graphene.String(required=False)

    occurrence = graphene.Field(Occurrence.Connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        errors = []
        form = OccurrenceCreateForm(input, request.FILES)
        if form.is_valid():
            occurrence = Occurrence._meta.model()
            occurrence.author = request.user.document
            occurrence.when = input.get('when')
            occurrence.where = input.get('where')
            occurrence.notes = input.get('notes')
            occurrence.save(request=request)

            for image_uploaded in form.cleaned_data['images']:
                image = ImageModel(image=image_uploaded)
                image.save(request=request)
                occurrence.images.add(image.document)

            return OccurrenceCreate(
                occurrence=Occurrence.Connection.Edge(
                    node=occurrence,
                    cursor=offset_to_cursor(0)),
            )
        else:
            errors = form_erros(form, errors)
        return OccurrenceCreate(errors=errors)


class SuggestionIDCreate(Mutation):
    class Input:
        occurrence = graphene.ID(required=True)
        identity = graphene.ID(required=True)
        notes = graphene.String(required=False)

    occurrence = graphene.Field(Occurrence)
    suggestionID = graphene.Field(SuggestionID.Connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        suggestion = SuggestionID._meta.model()
        suggestion.author = request.user.document

        gid_type, gid = from_global_id(input.get('occurrence'))
        suggestion.occurrence = Document._meta.model.objects.get(pk=gid)

        gid_type, gid = from_global_id(input.get('identity'))
        suggestion.identity = Document._meta.model.objects.get(pk=gid)

        suggestion.notes = input.get('notes')
        suggestion.save(request=request)

        return SuggestionIDCreate(
            occurrence=suggestion.occurrence.get_object(),
            suggestionID=SuggestionID.Connection.Edge(
                node=suggestion, cursor=offset_to_cursor(0)
            ),
        )
