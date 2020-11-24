import graphene
import django_filters
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth.hashers import make_password
from random import shuffle

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import (
    RANK_CHOICES, RANK_GENUS, RANK_SPECIES,
    LifeNode as LifeNodeModel,
    CommonName as CommonNameModel,
    Characteristic as CharacteristicModel
)
from accounts.models_graphql import User
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image
from tags.models_graphql import Tag
from backend.fields import GetBy


class Rank(graphene.Enum):
    KINGDOM = 10
    PHYLUM = 20
    CLASS = 30
    ORDER = 40
    FAMILY = 50
    GENUS = 60
    SPECIES = 70
    INFRASPECIES = 80
    VARIETY = 100

    @property
    def description(self):
        return dict(RANK_CHOICES)[self._value_]


class Edibility(graphene.Enum):
    # I will monitor any future ingestions of these,
    # can be experienced minor discomfort at least once after eating them.
    BAD = -1

    # Should be regarded as inedible.
    # NONE = 0

    # very minor uses found, or edible without much information on it
    SOME = 1

    # reasonably useful plant; worth collecting;
    # may be lacking in flavor or texture, but not both.
    POOR = 2

    # could be grown as standard crops, very good,
    # with distinctive flavor and texture.
    FAIR = 3

    # very useful plants
    GOOD = 4

    # great value. A very subjective evaluation.
    # Excellent in both flavor and texture;
    EXCELLENT = 5

    @property
    def description(self):
        return EDIBILITY_CHOICES.get(self._value_, '')


EDIBILITY_CHOICES = {
    Edibility.BAD._value_: "Não",
    Edibility.SOME._value_: "Sim (falta informação)",
    Edibility.POOR._value_: "Ruim",
    Edibility.FAIR._value_: "Rasoavel",
    Edibility.GOOD._value_: "Boa",
    Edibility.EXCELLENT._value_: "Excelente",
}


EDIBILITY_CHOICES_DESCRIPTION = {
    Edibility.BAD._value_: "Pode causar leve desconforto, ou consumir cozido",
    Edibility.SOME._value_: "Com pouca informação ou utilidade, ou consumir cozido",
    Edibility.POOR._value_: "Uil mas falta sabor ou textura, ou consumir cozido",
    Edibility.FAIR._value_: "Da pra comer em pouca quantidade",
    Edibility.GOOD._value_: "Util e saboroso",
    Edibility.EXCELLENT._value_: "Excelente sabor e textura",
}


def get_display(config, value, default=""):
    return dict(config).get(value, default)


def get_array_display(config, values) :
    l = []
    for value in values:
        l.append(get_display(config, value, value))
    return l


def get_collection_item_type():
    from lists.models_graphql import CollectionItem
    return CollectionItem


def get_wish_item_type():
    from lists.models_graphql import WishItem
    return WishItem


class CommonNamesFilter(django_filters.FilterSet):
    language = django_filters.CharFilter(field_name='language')
    country = django_filters.CharFilter(field_name='country')
    order = django_filters.OrderingFilter(
        choices=(
            ('avg', 'Media'),
        ),
        fields={
            'document__votestats__sum_values': 'avg',
        },
    )


class LifeNode(DjangoObjectType, DocumentBase):
    parent = graphene.Field(lambda: LifeNode)
    parents = graphene.List(lambda: LifeNode)
    rank = graphene.Field(Rank)
    rankDisplay = graphene.String()

    flower_colors = graphene.List(graphene.String)
    flower_types = graphene.List(graphene.String)
    fruit_type = graphene.List(graphene.String)
    growth_habit = graphene.List(graphene.String)
    phyllotaxy = graphene.String()
    leaf_type = graphene.String()
    leaf_texture = graphene.List(graphene.String)
    threatened = graphene.String()
    habitat = graphene.List(graphene.String)
    endemism = graphene.List(graphene.String)

    edibility = graphene.Field(Edibility)
    edibilityDisplay = graphene.String()

    commonNames = DjangoFilterConnectionField(lambda: CommonName, filterset_class=CommonNamesFilter)
    children = DjangoConnectionField(lambda: LifeNode)
    images = DjangoConnectionField(Image)
    characteristics = DjangoConnectionField(lambda: Characteristic)

    commonName = graphene.Field(lambda: CommonName)

    myCollectionItem = graphene.Field(get_collection_item_type)
    myWishItem = graphene.Field(get_wish_item_type)

    collectionList = DjangoConnectionField(get_collection_item_type)
    wishList = DjangoConnectionField(get_wish_item_type)

    class Meta:
        model = LifeNodeModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        filter_fields = []
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_parent(self, info):
        if self.parent:
            return self.parent.get_object()

    def resolve_parents(self, info):
        def get_parents(obj):
            parents = []
            if obj.parent:
                parent = obj.parent.get_object()
                parents.append(parent)
                parents.extend(get_parents(parent))
            return parents
        return get_parents(self)

    def resolve_rankDisplay(self, info):
        return self.get_rank_display()

    def resolve_edibilityDisplay(self, info):
        return EDIBILITY_CHOICES.get(self.edibility, '')

    def resolve_commonNames(self, info, **kwargs):
        return CommonName._meta.model.objects.filter(
            document_id__in=self.commonNames.values_list('id', flat=True)
        )

    def resolve_commonName(self, info):
        return CommonName._meta.model.objects.filter(
            document_id__in=self.commonNames.values_list('id', flat=True),
            language="por",
        ).order_by('-document__votestats__sum_values').first()

    def resolve_children(self, info, **kwargs):
        return LifeNode._meta.model.objects.filter(
            parent=self.document
        ).order_by('title')

    def resolve_images(self, info, **kwargs):
        return Image._meta.model.objects.filter(
            document_id__in=self.images.values_list('id', flat=True)
        )

    def resolve_characteristics(self, info, **kwargs):
        return Characteristic._meta.model.objects.filter(
            lifeNode=self.document
        )
    
    def resolve_myCollectionItem(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            return None

        CollectionItem = get_collection_item_type()
        return CollectionItem._meta.model.objects.filter(
            plant_id=self.document_id,
            user_id=info.context.user.document_id
        ).first()

    def resolve_myWishItem(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            return None

        WishItem = get_wish_item_type()
        return WishItem._meta.model.objects.filter(
            plant_id=self.document_id,
            user_id=info.context.user.document_id
        ).first()

    def resolve_collectionList(self, info, **kwargs):
        CollectionItem = get_collection_item_type()
        return CollectionItem._meta.model.objects.filter(
            plant=self.document_id
        ).order_by('-document__created_at')

    def resolve_wishList(self, info, **kwargs):
        WishItem = get_wish_item_type()
        return WishItem._meta.model.objects.filter(
            plant=self.document_id,
        ).order_by('-document__created_at')

    def resolve_threatened(self, info):
        return self.get_threatened_display()

    def resolve_phyllotaxy(self, info):
        return self.get_phyllotaxy_display()

    def resolve_leaf_type(self, info):
        return self.get_leaf_type_display()

    def resolve_leaf_texture(self, info):
        return get_array_display(LEAF_TEXTURE_CHOICES, self.leaf_texture)

    def resolve_growth_habit(self, info):
        return get_array_display(GROWTH_HABIT_CHOICES, self.growth_habit)

    def resolve_fruit_type(self, info):
        return get_array_display(FRUIT_TYPES_CHOICES, self.fruit_type)

    def resolve_flower_types(self, info):
        return get_array_display(FLOWER_TYPES_CHOICES, self.flower_types)

    def resolve_flower_colors(self, info):
        return get_array_display(COLOR_CHOICES, self.flower_color)


class CommonName(DjangoObjectType, DocumentBase):
    class Meta:
        model = CommonNameModel
        interfaces = (Node, DocumentNode, VotesNode)
        connection_class = CountedConnection


class Characteristic(DjangoObjectType, DocumentBase):
    tag = graphene.Field(lambda: Tag)
    title = graphene.String()

    class Meta:
        model = CharacteristicModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        connection_class = CountedConnection

    def resolve_tag(self, info):
        return self._get_tag()

    def resolve_title(self, info):
        return self._get_tag().title


class Quizz(graphene.ObjectType):
    image = graphene.Field(Image)
    choices = graphene.List(LifeNode)
    correct = graphene.String()

    class Meta:
        interfaces = (Node, )


def generate_quiz(root, info):
    image = Image._meta.model.objects.filter(
        document__lifeNode_image__rank__in=(RANK_GENUS, RANK_SPECIES)
    ).order_by('?').first()

    lifeNode = image.document.lifeNode_image.first()
    if lifeNode.rank == RANK_SPECIES:
        correct = lifeNode.parent.get_object()
    elif lifeNode.rank == RANK_GENUS:
        correct = lifeNode

    other_choices = LifeNode._meta.model.objects.filter(
        rank=RANK_GENUS
    ).exclude(document=correct.document).order_by('?')[:4]

    choices = [correct]
    for c in other_choices:
        choices.append(c)

    shuffle(choices)

    return Quizz(
        id=1,
        image=image,
        choices=choices,
        correct=make_password("%d" % correct.document_id, hasher='sha1')
    )


class Query(object):
    lifeNode = Node.Field(LifeNode)
    lifeNodeByIntID = GetBy(LifeNode, document_id=graphene.Int(required=True))
    allLifeNode = DjangoFilterConnectionField(LifeNode, args={
        'rank': graphene.Argument(graphene.List(Rank), required=False),
        'edibility': graphene.Argument(Edibility, required=False),
        'search': graphene.Argument(graphene.String, required=False),
        'order_by': graphene.Argument(graphene.String, required=False),
        'edibles': graphene.Argument(graphene.Boolean, required=False),
        'phyllotaxy': graphene.Argument(graphene.String, required=False),
        'leaf_type': graphene.Argument(graphene.String, required=False),
        'threatened': graphene.Argument(graphene.String, required=False),
        'flower_colors': graphene.Argument(graphene.List(graphene.String), required=False),
        'flower_types': graphene.Argument(graphene.List(graphene.String), required=False),
        'fruit_type': graphene.Argument(graphene.List(graphene.String), required=False),
        'growth_habit': graphene.Argument(graphene.List(graphene.String), required=False),
        'leaf_texture': graphene.Argument(graphene.List(graphene.String), required=False),
        'habitat': graphene.Argument(graphene.List(graphene.String), required=False),
    }, total_found2=graphene.Int(required=False, name='totalFound2'))

    lifeNodeQuizz = graphene.Field(Quizz, resolver=generate_quiz)

    def resolve_allLifeNode(self, info, **args):
        qs = LifeNode._meta.model.objects.all()
        if 'rank' in args:
            qs = qs.filter(rank__in=args['rank'])
        if 'edibility' in args:
            qs = qs.filter(edibility=args['edibility'])
        if 'edibles' in args and bool(args['edibles']):
            qs = qs.filter(edibility__gte=1)
        if 'phyllotaxy' in args:
            qs = qs.filter(phyllotaxy=args['phyllotaxy'])
        if 'leaf_type' in args:
            qs = qs.filter(leaf_type=args['leaf_type'])
        if 'threatened' in args:
            qs = qs.filter(threatened=args['threatened'])
        if 'flower_colors' in args:
            qs = qs.filter(flower_colors__contains=args['flower_colors'])
        if 'flower_types' in args:
            qs = qs.filter(flower_types__contains=args['flower_types'])
        if 'fruit_type' in args:
            qs = qs.filter(fruit_type__contains=args['fruit_type'])
        if 'growth_habit' in args:
            qs = qs.filter(growth_habit__contains=args['growth_habit'])
        if 'leaf_texture' in args:
            qs = qs.filter(leaf_texture__contains=args['leaf_texture'])
        if 'habitat' in args:
            qs = qs.filter(habitat__contains=args['habitat'])
        if 'search' in args and len(args['search']) > 2:
            s = args['search'].strip()
            q_objects = Q(title__icontains=s)

            commonNames = CommonName._meta.model.objects.filter(
                name__icontains=s
            ).distinct().values_list('document_id', flat=True)

            if len(commonNames) > 0:
                q_objects |= Q(commonNames__id__in=commonNames)

            qs = qs.filter(q_objects)
            return qs.distinct()

        order_by = args.get('order_by')

        if order_by == '-wish_count':
            qs = qs.filter(document__liststats__isnull=False)
            qs = qs.order_by('-document__liststats__wish_count')

        if order_by == '-collection_count':
            qs = qs.filter(document__liststats__isnull=False)
            qs = qs.order_by('-document__liststats__collection_count')

        if not order_by:
            qs = qs.order_by('document_id')

        return qs.distinct()
