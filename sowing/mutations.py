import graphene
import graphql_geojson

from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django import forms
from django.core.exceptions import ValidationError
from multiupload.fields import MultiImageField

from backend.fields import Error
from backend.mutations import Mutation
from db.models_graphql import Document
from utils.forms import form_erros
from images.models import Image as ImageModel
from .models_graphql import Sowing


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


class SowingCreateForm(forms.Form):
    images = MyMultiImageField(min_num=0, required=False)


class SowingCreate(Mutation):
    class Input:
        where = graphene.String(required=False)
        notes = graphene.String(required=False)
        location = graphene.Field(graphql_geojson.Geometry, required=False)
        species = graphene.List(graphene.ID, required=False)
        name = graphene.String(required=False)
        email = graphene.String(required=False)

    sowing = graphene.Field(Sowing._meta.connection.Edge)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        errors = []
        form = SowingCreateForm(input, info.context.FILES)
        if form.is_valid():
            sowing = Sowing._meta.model()

            # If authenticated, set author; otherwise capture provided name/email
            if hasattr(info.context, 'user') and info.context.user.is_authenticated:
                sowing.author = info.context.user.document
            else:
                sowing.author = None
                sowing.author_name = input.get('name')
                sowing.author_email = input.get('email')

            sowing.where = input.get('where')
            sowing.notes = input.get('notes')

            location = input.get('location')
            if location:
                sowing.location = location

            sowing.save(request=info.context)

            # Species list
            species_ids = input.get('species') or []
            for sid in species_ids:
                gid_type, gid = from_global_id(sid)
                species_doc = Document._meta.model.objects.get(pk=gid)
                sowing.species.add(species_doc)

            # Images upload
            for image_uploaded in form.cleaned_data['images']:
                image = ImageModel(image=image_uploaded)
                image.save(request=info.context)
                sowing.images.add(image.document)

            return SowingCreate(
                sowing=Sowing._meta.connection.Edge(
                    node=sowing,
                    cursor=offset_to_cursor(0)
                )
            )
        else:
            errors = form_erros(form, errors)
        return SowingCreate(errors=errors)

