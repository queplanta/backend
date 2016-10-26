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
from .models_graphql import WhatIsThis, SuggestionID


class WhatIsThisCreateForm(forms.Form):
    images = MultiImageField(min_num=1)


class WhatIsThisCreate(Mutation):
    class Input:
        when = graphene.String(required=False)
        where = graphene.String(required=False)
        notes = graphene.String(required=False)

    whatIsThis = graphene.Field(WhatIsThis.Connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        errors = []
        form = WhatIsThisCreateForm(input, request.FILES)
        if form.is_valid():
            what = WhatIsThis._meta.model()
            what.author = request.user.document
            what.when = input.get('when')
            what.where = input.get('where')
            what.notes = input.get('notes')
            what.save(request=request)

            for image_uploaded in form.cleaned_data['images']:
                image = ImageModel(image=image_uploaded)
                image.save(request=request)
                what.images.add(image.document)

            return WhatIsThisCreate(
                whatIsThis=WhatIsThis.Connection.Edge(
                    node=what,
                    cursor=offset_to_cursor(0)),
            )
        else:
            errors = form_erros(form, errors)
        return WhatIsThisCreate(errors=errors)


class SuggestionIDCreate(Mutation):
    class Input:
        whatIsThis = graphene.ID(required=True)
        identification = graphene.ID(required=True)
        notes = graphene.String(required=False)

    suggestionID = graphene.Field(SuggestionID.Connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        suggestion = SuggestionID._meta.model()
        suggestion.author = request.user.document

        gid_type, gid = from_global_id(input.get('whatIsThis'))
        suggestion.whatisthis = Document._meta.model.objects.get(pk=gid)

        gid_type, gid = from_global_id(input.get('identification'))
        suggestion.identification = Document._meta.model.objects.get(pk=gid)

        suggestion.notes = input.get('notes')
        suggestion.save(request=request)

        return SuggestionIDCreate(
            suggestionID=SuggestionID.Connection.Edge(
                node=suggestion, cursor=offset_to_cursor(0)
            ),
        )
