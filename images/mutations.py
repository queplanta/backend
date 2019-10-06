import graphene
from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django import forms
from django.utils.datastructures import MultiValueDict

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.models_graphql import Document
from backend.mutations import Mutation
from images.models import Image as ImageModel
from images.models_graphql import Image, Imaging


class ImageForm(forms.Form):
    image = forms.ImageField(required=True)
    description = forms.CharField(required=False)


class ImageInput(graphene.InputObjectType):
    description = graphene.String(required=False)


class ImageCreate(Mutation):
    class Input:
        parent = graphene.ID(required=True)
        description = graphene.String(required=False)

    image = graphene.Field(Image._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('parent'))
        node = Document._meta.model.objects.get(pk=gid)

        error = has_permission(cls, info.context, node.get_object(), 'add_image')
        if error:
            return error

        errors = []
        image = None

        form = ImageForm(input, MultiValueDict({
            'image': info.context.FILES.getlist('image')
        }))
        if form.is_valid():
            data = form.cleaned_data
            image = ImageModel(
                parent=node,
                image=data['image'],
                description=data['description']
            )
            image.save(request=info.context)
        else:
            errors = form_erros(form, errors)

        return ImageCreate(
            image=Image._meta.connection.Edge(
                node=image,
                cursor=offset_to_cursor(0)
            ) if image else None,
            errors=errors,
        )


class ImageEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        description = graphene.String()

    image = graphene.Field(Image)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        node = Image._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, node, 'edit')
        if error:
            return error

        node.description = input.get('description')
        node.save(request=info.context)
        return ImageEdit(image=node)


class ImageDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    imageDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        node = Image._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, node, 'delete')
        if error:
            return error

        node.delete(request=info.context)

        return ImageDelete(imageDeletedID=input.get('id'))


class Mutations(object):
    imageCreate = ImageCreate.Field()
    imageEdit = ImageEdit.Field()
    imageDelete = ImageDelete.Field()
