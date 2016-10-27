import graphene

from sorl.thumbnail import get_thumbnail


class File(graphene.ObjectType):
    url = graphene.String(required=True)
    # contentType = graphene.String()
    # bytes = graphene.Int()


class Thumbnail(graphene.Field):
    def __init__(self, type=File, **kwargs):
        kwargs.update({
            'args': {
                'width': graphene.Argument(graphene.Int, required=True),
                'height': graphene.Argument(graphene.Int, required=True),
            }
        })

        return super(Thumbnail, self).__init__(type, **kwargs)

    def get_resolver(self, parent_resolver):
        resolver = self.resolver or parent_resolver

        def built_thumbnail(instance, args, context, info):
            instance = resolver(instance, args, context, info)
            url = get_thumbnail(instance, '%(width)dx%(height)d' % args,
                                crop='center', quality=90).url
            return File(url=url)

        return built_thumbnail
