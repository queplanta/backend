import graphene
import graphql_geojson

from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django import forms
from django.core.exceptions import ValidationError
from multiupload.fields import MultiImageField

from accounts.decorators import login_required
from accounts.permissions import has_permission
from backend.mutations import Mutation
from db.models_graphql import Document
from utils.forms import form_erros
from images.models import Image as ImageModel
from .models_graphql import Occurrence, SuggestionID


class MyMultiImageField(MultiImageField):
    def run_validators(self, value):
        if value in self.empty_values:
            return
        errors = []
        for v in self.validators:
            for item in value:
                try:
                    v(item)
                except ValidationError as e:
                    if hasattr(e, 'code') and e.code in self.error_messages:
                        e.message = self.error_messages[e.code]
                    errors.extend(e.error_list)
        if errors:
            raise ValidationError(errors)


class OccurrenceCreateForm(forms.Form):
    images = MyMultiImageField(min_num=0, required=False)


class OccurrenceCreate(Mutation):
    class Input:
        when = graphene.String(required=False)
        where = graphene.String(required=False)
        notes = graphene.String(required=False)
        life_id = graphene.ID(required=False)
        location = graphene.Field(graphql_geojson.Geometry, required=False)

    occurrence = graphene.Field(Occurrence._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        errors = []
        form = OccurrenceCreateForm(input, info.context.FILES)
        if form.is_valid():
            occurrence = Occurrence._meta.model()
            occurrence.author = info.context.user.document
            occurrence.when = input.get('when')
            occurrence.where = input.get('where')
            occurrence.notes = input.get('notes')

            location = input.get('location')
            if location:
                occurrence.location = location

            life_id = input.get('life_id')
            if life_id:
                life_gid_type, life_gid = from_global_id(life_id)
                occurrence.identity = Document._meta.model.objects.get(
                    pk=life_gid)

            occurrence.save(request=info.context)

            for image_uploaded in form.cleaned_data['images']:
                image = ImageModel(image=image_uploaded)
                image.save(request=info.context)
                occurrence.images.add(image.document)

            return OccurrenceCreate(
                occurrence=Occurrence._meta.connection.Edge(
                    node=occurrence,
                    cursor=offset_to_cursor(0)),
            )
        else:
            errors = form_erros(form, errors)
        return OccurrenceCreate(errors=errors)


class OccurrenceDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    occurenceDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        occurence = Occurrence._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, occurence, 'delete')
        if error:
            return error

        occurence.delete(request=info.context)

        return OccurrenceDelete(occurenceDeletedID=input.get('id'))


class WhatIsThisCreateForm(forms.Form):
    images = MyMultiImageField(min_num=1)


class WhatIsThisCreate(Mutation):
    class Input:
        when = graphene.String(required=False)
        where = graphene.String(required=False)
        notes = graphene.String(required=False)
        location = graphene.Field(graphql_geojson.Geometry, required=False)

    occurrence = graphene.Field(Occurrence._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        errors = []
        form = WhatIsThisCreateForm(input, info.context.FILES)
        if form.is_valid():
            occurrence = Occurrence._meta.model()
            occurrence.author = info.context.user.document
            occurrence.when = input.get('when')
            occurrence.where = input.get('where')
            occurrence.notes = input.get('notes')
            occurrence.save(request=info.context)

            for image_uploaded in form.cleaned_data['images']:
                image = ImageModel(image=image_uploaded)
                image.save(request=info.context)
                occurrence.images.add(image.document)

            return WhatIsThisCreate(
                occurrence=Occurrence._meta.connection.Edge(
                    node=occurrence,
                    cursor=offset_to_cursor(0)),
            )
        else:
            errors = form_erros(form, errors)
        return WhatIsThisCreate(errors=errors)


class WhatIsThisIdentify(Mutation):
    class Input:
        id = graphene.ID(required=True)
        life_id = graphene.ID(required=True)

    occurrence = graphene.Field(Occurrence._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        occurence = Occurrence._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, occurence, 'identify')
        if error:
            return error

        life_id = input.get('life_id')
        life_gid_type, life_gid = from_global_id(life_id)
        occurrence.identity = Document._meta.model.objects.get(
            pk=life_gid)

        occurence.save(request=info.context, message="define identificação")

        return WhatIsThisIdentify(occurrence=occurrence)


class SuggestionIDCreate(Mutation):
    class Input:
        occurrence = graphene.ID(required=True)
        identity = graphene.ID(required=True)
        notes = graphene.String(required=False)

    occurrence = graphene.Field(Occurrence)
    suggestionID = graphene.Field(SuggestionID._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        suggestion = SuggestionID._meta.model()
        suggestion.author = info.context.user.document

        gid_type, gid = from_global_id(input.get('occurrence'))
        suggestion.occurrence = Document._meta.model.objects.get(pk=gid)

        gid_type, gid = from_global_id(input.get('identity'))
        suggestion.identity = Document._meta.model.objects.get(pk=gid)

        suggestion.notes = input.get('notes')
        suggestion.save(request=info.context)

        return SuggestionIDCreate(
            occurrence=suggestion.occurrence.get_object(),
            suggestionID=SuggestionID._meta.connection.Edge(
                node=suggestion, cursor=offset_to_cursor(0)
            ),
        )


class SuggestionIDDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    suggestionDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        suggestion = SuggestionID._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, suggestion, 'delete')
        if error:
            return error

        suggestion.delete(request=request)

        return SuggestionIDDelete(suggestionDeletedID=input.get('id'))
