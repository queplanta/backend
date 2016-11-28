import graphene
from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django import forms
from django.utils.datastructures import MultiValueDict
from django.utils.text import slugify

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.models_graphql import Document
from backend.mutations import Mutation
from .models_graphql import LifeNode, Characteristic
from .models import (
    RANK_BY_STRING, CommonName,
    LifeNode as LifeNodeModel,
    Characteristic as CharacteristicModel
)
from tags.models import Tag as TagModel
from images.models import Image as ImageModel


class ImageForm(forms.Form):
    image = forms.ImageField(required=True)
    description = forms.CharField(required=False)


def node_save(node, args, request):
    node.title = args.get('title', node.title)
    node.description = args.get('description', node.description)
    node.gbif_id = args.get('gbif_id', node.gbif_id)
    try:
        node.rank = RANK_BY_STRING[args.get('rank').lower()]
    except KeyError:
        pass

    parent_id = args.get('parent')
    if parent_id:
        gid_type, gid = from_global_id(parent_id)
        node.parent = Document._meta.model.objects.get(pk=gid)

    node.save(request=request)

    commonNames = args.get('commonNames', [])
    for commonNameDict in commonNames:
        commonName_str = commonNameDict['name'].strip(' \t\n\r')

        if len(commonName_str) == 0:
            # don't save empty
            continue

        try:
            commonName = CommonName.objects.get(
                name=commonName_str,
                document__lifeNode_commonName=node
            )
        except CommonName.DoesNotExist:
            commonName = CommonName(
                name=commonName_str,
                language=commonNameDict['language']
            )
            commonName.save(request=request)
        node.commonNames.add(commonName.document)

    imagesToAdd = args.get('imagesToAdd', [])
    for imageToAdd in imagesToAdd:
        form = ImageForm(imageToAdd, MultiValueDict({
            'image': request.FILES.getlist(imageToAdd['field'])
        }))
        if form.is_valid():
            data = form.cleaned_data
            image = ImageModel(
                image=data['image'],
                description=data['description']
            )
            image.save(request=request)
            node.images.add(image.document)

    return node


class CommonNameInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    language = graphene.String(required=False)


class ImageInput(graphene.InputObjectType):
    field = graphene.String(required=True)
    description = graphene.String(required=False)


class LifeNodeCreate(Mutation):
    class Input:
        title = graphene.String(required=True)
        description = graphene.String()
        rank = graphene.String(required=True)
        parent = graphene.ID()
        gbif_id = graphene.Int()
        commonNames = graphene.List(CommonNameInput)
        imagesToAdd = graphene.List(ImageInput)

    lifeNode = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        node = LifeNode._meta.model()
        node = node_save(node, input, request)
        return LifeNodeCreate(lifeNode=node)


class LifeNodeEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        rank = graphene.String()
        parent = graphene.ID()
        gbif_id = graphene.Int()
        commonNames = graphene.List(CommonNameInput)
        imagesToAdd = graphene.List(ImageInput)

    lifeNode = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, node, 'edit')
        if error:
            return error

        node = node_save(node, input, request)
        return LifeNodeEdit(lifeNode=node)


class LifeNodeDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    lifeNodeDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, node, 'delete')
        if error:
            return error

        node.delete(request=request)

        return LifeNodeDelete(lifeNodeDeletedID=input.get('id'))


class SpeciesCreate(Mutation):
    class Input:
        commonNames = graphene.String(required=False)
        species = graphene.String(required=True)
        genus = graphene.String(required=True)
        family = graphene.String(required=False)

    species = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        genus_qs = LifeNodeModel.objects.filter(
            title__iexact=input.get('genus'),
            rank=RANK_BY_STRING['genus'])

        genus = None
        family = None

        if genus_qs.count() > 0:
            genus = genus_qs[0]
        elif len(input.get('genus')) > 0:
            family_qs = LifeNodeModel.objects.filter(
                title__iexact=input.get('family'),
                rank=RANK_BY_STRING['family'])
            if family_qs.count() > 0:
                family = family_qs[0]
            elif len(input.get('family')) > 0:
                family = LifeNodeModel(
                    rank=RANK_BY_STRING['family'],
                    title=input.get('family')
                )
                family.save(request=request)
            genus = LifeNodeModel(
                rank=RANK_BY_STRING['genus'],
                title=input.get('genus'),
                parent=family.document if family else None
            )
            genus.save(request=request)

        species = LifeNodeModel(
            parent=genus.document if genus else None,
            rank=RANK_BY_STRING['species'],
            title=input.get('species'),
        )
        species.save(request=request)

        commonNames_raw = input.get('commonNames', '')
        for commonName_str in commonNames_raw.split(','):
            commonName_str = commonName_str.strip(' \t\n\r')

            if len(commonName_str) == 0:
                # don't save empty
                continue

            try:
                commonName = CommonName.objects.get(name=commonName_str)
            except CommonName.DoesNotExist:
                commonName = CommonName(
                    name=commonName_str,
                )
                commonName.save(request=request)
            species.commonNames.add(commonName.document)

        return SpeciesCreate(species=species)


class CharacteristicAdd(Mutation):
    class Input:
        lifeNode = graphene.ID(required=True)
        title = graphene.String(required=True)
        value = graphene.String()

    lifeNode = graphene.Field(LifeNode)
    characteristic = graphene.Field(Characteristic.Connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('lifeNode'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, node, 'edit')
        if error:
            return error

        tag_title = input.get('title').strip(' \t\n\r')
        tag_slug = slugify(tag_title)

        try:
            tag = TagModel.objects.get(slug=tag_slug)
        except TagModel.DoesNotExist:
            tag = TagModel(
                title=tag_title,
                slug=tag_slug,
            )
            tag.save(request=request)

        c = CharacteristicModel(
            tag=tag.document,
            lifeNode=node.document,
            value=input.get('value')
        )
        c.save(request=request)

        return CharacteristicAdd(
            lifeNode=node,
            characteristic=Characteristic.Connection.Edge(
                node=c, cursor=offset_to_cursor(0))
        )
