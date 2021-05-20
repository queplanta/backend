import graphene
from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django import forms
from django.utils.datastructures import MultiValueDict
from django.utils.text import slugify
from django.contrib.auth.hashers import check_password

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.models_graphql import Document
from backend.mutations import Mutation
from .models_graphql import (
    LifeNode, Characteristic, Rank, Edibility,
    FlowerColor, FlowerType, GrowthHabit,
    Quizz, generate_quiz, CommonName
)
from .models import (
    RANK_BY_STRING, CommonName as CommonNameModel,
    LifeNode as LifeNodeModel,
    Characteristic as CharacteristicModel
)
from tags.models import Tag as TagModel
from images.models import Image as ImageModel


class ImageForm(forms.Form):
    image = forms.ImageField(required=True)
    description = forms.CharField(required=False)


def node_save(node, args, info):
    node.title = args.get('title', node.title)
    node.description = args.get('description', node.description)
    node.gbif_id = args.get('gbif_id', node.gbif_id)
    node.rank = args.get('rank', node.rank)
    node.edibility = args.get('edibility', node.edibility)

    node.flower_colors = args.get('flower_colors', node.flower_colors)
    node.flower_types = args.get('flower_types', node.flower_types)
    node.growth_habit = args.get('growth_habit', node.growth_habit)

    node.height = args.get('height', node.height)
    node.sun = args.get('sun', node.sun)
    node.spread = args.get('spread', node.spread)
    node.time_to_fruit = args.get('time_to_fruit', node.time_to_fruit)

    node.succession = args.get('succession', node.succession)
    node.growth_rate = args.get('growth_rate', node.growth_rate)
    node.fruit_type = args.get('fruit_type', node.fruit_type)
    node.leaf_type = args.get('leaf_type', node.leaf_type)
    node.leaf_texture = args.get('leaf_texture', node.leaf_texture)
    node.phyllotaxy = args.get('phyllotaxy', node.phyllotaxy)
    node.threatened = args.get('threatened', node.threatened)

    parent_id = args.get('parent')
    if parent_id:
        gid_type, gid = from_global_id(parent_id)
        node.parent = Document._meta.model.objects.get(pk=gid)

    prev_images = []
    if node.pk:
        prev_images = node.images.values_list('id', flat=True)

    prev_commonNames = []
    if node.pk:
        prev_commonNames = node.commonNames.values_list('id', flat=True)

    node.save(request=info.context)

    for prev_img_id in prev_images:
        node.images.add(prev_img_id)

    node.commonNames.clear()
    for prev_name_id in prev_commonNames:
        node.commonNames.add(prev_name_id)

    commonNames = args.get('commonNames', [])
    for commonNameDict in commonNames:
        commonName_id = commonNameDict.get('id', '').strip(' \t\n\r')
        commonName_str = commonNameDict['name'].strip(' \t\n\r')

        if len(commonName_str) == 0:
            # don't save empty
            continue

        if len(commonName_id) > 0:
            cn_gid_type, cn_gid = from_global_id(commonName_id)
            get = {'document_id': cn_gid}
        else:
            get = {
                'name': commonName_str,
                'document__lifeNode_commonName': node
            }

        try:
            commonName = CommonNameModel.objects.get(**get)
        except CommonNameModel.DoesNotExist:
            commonName = CommonNameModel()

        commonName.name = commonName_str
        commonName.language = commonNameDict['language']
        commonName.save(request=info.context)
        if commonName.document_id not in prev_commonNames:
            node.commonNames.add(commonName.document)

    imagesToAdd = args.get('imagesToAdd', [])
    for imageToAdd in imagesToAdd:
        form = ImageForm(imageToAdd, MultiValueDict({
            'image': info.context.FILES.getlist(imageToAdd['field'])
        }))
        if form.is_valid():
            data = form.cleaned_data
            image = ImageModel(
                image=data['image'],
                description=data['description']
            )
            image.save(request=info.context)
            node.images.add(image.document)

    return node


class CommonNameInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    name = graphene.String(required=True)
    language = graphene.String(required=False)


class ImageInput(graphene.InputObjectType):
    field = graphene.String(required=True)
    description = graphene.String(required=False)


class LifeNodeCreate(Mutation):
    class Input:
        title = graphene.String(required=True)
        description = graphene.String()
        rank = graphene.Field(Rank, required=True)
        edibility = graphene.Field(Edibility)
        flower_colors = graphene.Field(FlowerColor)
        flower_types = graphene.Field(FlowerType)

        growth_habit = graphene.Field(GrowthHabit)
        parent = graphene.ID()
        gbif_id = graphene.Int()
        commonNames = graphene.List(CommonNameInput)
        imagesToAdd = graphene.List(ImageInput)

    lifeNode = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        node = LifeNode._meta.model()
        node = node_save(node, input, info)
        return LifeNodeCreate(lifeNode=node)


class LifeNodeEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        rank = graphene.Field(Rank)
        edibility = graphene.Field(Edibility)
        flower_colors = graphene.List(FlowerColor)
        flower_types = graphene.List(FlowerType)
        growth_habit = graphene.List(GrowthHabit)
        parent = graphene.ID()
        gbif_id = graphene.Int()
        commonNames = graphene.List(CommonNameInput)
        imagesToAdd = graphene.List(ImageInput)

    lifeNode = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, node, 'edit')
        if error:
            return error

        node = node_save(node, input, info)
        return LifeNodeEdit(lifeNode=node)


class LifeNodeDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    lifeNodeDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, node, 'delete')
        if error:
            return error

        node.delete(request=info.context)

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
    def mutate_and_get_payload(cls, root, info, **input):
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
                family.save(request=info.context)
            genus = LifeNodeModel(
                rank=RANK_BY_STRING['genus'],
                title=input.get('genus'),
                parent=family.document if family else None
            )
            genus.save(request=info.context)

        species = LifeNodeModel(
            parent=genus.document if genus else None,
            rank=RANK_BY_STRING['species'],
            title=input.get('species'),
        )
        species.save(request=info.context)

        commonNames_raw = input.get('commonNames', '')
        for commonName_str in commonNames_raw.split(','):
            commonName_str = commonName_str.strip(' \t\n\r')

            if len(commonName_str) == 0:
                # don't save empty
                continue

            try:
                commonName = CommonNameModel.objects.get(name=commonName_str)
            except CommonNameModel.DoesNotExist:
                commonName = CommonNameModel(
                    name=commonName_str,
                )
                commonName.save(request=info.context)
            species.commonNames.add(commonName.document)

        return SpeciesCreate(species=species)


class CommonNameAdd(Mutation):
    class Input:
        lifeNode = graphene.ID(required=True)
        name = graphene.String(required=True)
        language = graphene.String()
        country = graphene.String()
        region = graphene.String()

    lifeNode = graphene.Field(LifeNode)
    commonName = graphene.Field(CommonName._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('lifeNode'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, node, 'edit')
        if error:
            return error

        try:
            common_name = CommonNameModel.objects.get(
                name=input.get('name'),
                language=input.get('language'),
                country=input.get('country'),
                region=input.get('region')
            )
        except CommonNameModel.DoesNotExist:
            common_name = CommonNameModel(
                name=input.get('name'),
                language=input.get('language'),
                country=input.get('country'),
                region=input.get('region')
            )
            common_name.save(request=info.context)

        node.commonNames.add(common_name.document)

        return CommonNameAdd(
            lifeNode=node,
            commonName=CommonName._meta.connection.Edge(
                node=common_name, cursor=offset_to_cursor(0))
        )


class CharacteristicAdd(Mutation):
    class Input:
        lifeNode = graphene.ID(required=True)
        title = graphene.String(required=True)
        value = graphene.String()

    lifeNode = graphene.Field(LifeNode)
    characteristic = graphene.Field(Characteristic._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('lifeNode'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, node, 'edit')
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
            tag.save(request=info.context)

        c = CharacteristicModel(
            tag=tag.document,
            lifeNode=node.document,
            value=input.get('value')
        )
        c.save(request=info.context)

        return CharacteristicAdd(
            lifeNode=node,
            characteristic=Characteristic._meta.connection.Edge(
                node=c, cursor=offset_to_cursor(0))
        )


class CheckQuizz(Mutation):
    class Input:
        choice = graphene.Int(required=True)
        correct = graphene.String(required=True)

    quizz = graphene.Field(Quizz)
    correct = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        correct = check_password(
            str(input.get('choice')),
            input.get('correct')
        )

        return CheckQuizz(
            correct=correct,
            quizz=generate_quiz(root, info)
        )


class Mutations(object):
    speciesCreate = SpeciesCreate.Field()
    lifeNodeCreate = LifeNodeCreate.Field()
    lifeNodeEdit = LifeNodeEdit.Field()
    lifeNodeDelete = LifeNodeDelete.Field()
    lifeNodeCharacteristicAdd = CharacteristicAdd.Field()
    lifeNodeCheckQuizz = CheckQuizz.Field()
    lifeNodeCommonNameAdd = CommonNameAdd.Field()
