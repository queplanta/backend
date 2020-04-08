from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField, limit_by_contenttype


RANK_KINGDOM = 10
RANK_PHYLUM = 20
RANK_CLASS = 30
RANK_ORDER = 40
RANK_FAMILY = 50
RANK_GENUS = 60
RANK_SPECIES = 70
RANK_INFRASPECIES = 80
RANK_VARIETY = 100

RANK_CHOICES = (
    (RANK_KINGDOM, _('Kingdom')),
    (RANK_PHYLUM, _('Phylum')),
    (RANK_CLASS, _('Class')),
    (RANK_ORDER, _('Order')),
    (RANK_FAMILY, _('Family')),
    (RANK_GENUS, _('Genus')),
    (RANK_SPECIES, _('Species')),
    (RANK_INFRASPECIES, _('Infraspecies')),
    (RANK_VARIETY, _('Variety')),
)

RANK_BY_STRING = {
    'kingdom': RANK_KINGDOM,
    'phylum': RANK_PHYLUM,
    'class': RANK_CLASS,
    'order': RANK_ORDER,
    'family': RANK_FAMILY,
    'genus': RANK_GENUS,
    'species': RANK_SPECIES,
    'infraspecies': RANK_INFRASPECIES,
    'variety': RANK_VARIETY,
}
RANK_STRING_BY_INT = {v: k for k, v in RANK_BY_STRING.items()}


class LifeNode(DocumentBase):
    rank = models.IntegerField(choices=RANK_CHOICES)
    parent = models.ForeignKey(DocumentID, related_name="children", null=True, on_delete=models.SET_NULL)

    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, null=True)
    description = models.TextField(null=True, blank=True)

    edibility = models.IntegerField(null=True)

    gbif_id = models.IntegerField(null=True, blank=True)

    commonNames = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('life.CommonName'),
        related_name='lifeNode_commonName'
    )

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='lifeNode_image'
    )



    #  body_parts = ManyToManyField(
    #      DocumentID,
    #      limit_choices_to=limit_by_contenttype('life.PlantBodyPart'),
    #      related_name='lifeNode_bodyPart'
    #  )

    # class Meta:
    #     unique_together = ("is_tip", "slug")

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) == 0:
            self.slug = slugify(self.title)
        return super(LifeNode, self).save(*args, **kwargs)


class CommonName(DocumentBase):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=3, null=True, blank=True)
    region = models.CharField(max_length=3, null=True, blank=True)

    REPUTATION_VALUE = 1


class Characteristic(DocumentBase):
    tag = models.ForeignKey(DocumentID, related_name="characteristic_tag", on_delete=models.CASCADE)
    lifeNode = models.ForeignKey(DocumentID,
                                 related_name="characteristic_lifeNode", on_delete=models.CASCADE)
    value = models.CharField(max_length=512, null=True)

    def _get_tag(self):
        if not hasattr(self, '_tag'):
            self._tag = self.tag.get_object()
        return self._tag


class DocumentAttribute(DocumentBase):
    document = models.ForeignKey(DocumentID, related_name="attributes", on_delete=models.CASCADE)
    attribute = models.ForeignKey(DocumentID, related_name="documentAttributes", null=True, on_delete=models.SET_NULL)

    strings_list = ArrayField(models.CharField(max_length=255), blank=True)

    integer = models.IntegerField(null=True)
    integer_range = IntegerRangeField(null=True)

    decimal = models.DecimalField(null=True)
    decimal_range = DecimalRangeField(null=True)

    many_to_many = ManyToManyField(
        DocumentID,
        related_name='bodyPart_type'
    )

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='bodyPart_image'
    )


class Attribute(models.Model):
    #  parent models.ForeignKey('self')
    #  # a ideia é poder ter flower.types flower.color
    # acho que nao precisa... a key pode ser assim com ponto (.)

    key = models.SlugField(max_length=512)
    content_type =
    value_type = integer, integer_range, relationship, relationship_list, decimal, decimal_range

    name = models.CharField(max_length=255)

    page = models.ForeignKey(DocumentID, related_name="attributes", on_delete=models.CASCADE)

    relationship_choices = ManyToManyField(
        DocumentID,
        related_name='relationship_choices_of_attributes'
    )


class Term(DocumentBase):
    name # used in links
    title # page title? seo
    slug
    # para conseguir usar Attribute para definir termos


class BodyPartType(DocumentBase):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=512)

    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) == 0:
            self.slug = slugify(self.title)
        return super(BodyPartType, self).save(*args, **kwargs)


"""
Plant {
    title # seria possibel gerar um schema com dados do banco de dados? A ideia á ter esses atributes como campos reais no modelo de dados
            assim value type / casting é feito pelo GraphQL, sem a necessidade de usar integer, interger_range etc...

    body: attributes(startswith: "body") { # caso quiser agrupadar
        key
        name
        value_type
        decimal
    }

    attributes(exclude: ["images"], exclude_startswith: "body") {
        key
        value
        /// ou integer, interget_range ... ?
        value_type
        version {
           id
           author
        }
    }

    author: attribute(key: "author") {
        relationship {
            ... on Author {
                name
            }
        }
    }

    images: attribute(key: "images") {
        relationship_list {
            edges {
                node {
                    ... on Image {
                        url 
                    }
                }
            }
        }
    }
}

No react podemos ter a pagina de versionamento generica para cada attribute value type ele renderiza um React.Component adequado.

Deve ser possivel extender o pagina de diff com:
<ListDiffAttributes
    customFieldComponent={{
        author: AuthorDiffComponent,
        images: ImagesDiffComponent
    }}
/>

Para lists, mostrar um diff assim:
    - Excluidos
        - 1, 2
    - Adicionados
        - 3, 4
    - Mantidos
        - 5, 6, 7, 8


Attributes management, admin, add, remove of edit should be managed by migrations
EVEN page its creation and relation
"""

