import graphene
from shortener import shortener
from shortener.models import UrlMap

from accounts.decorators import login_required


class Query(object):
    url_shortner = graphene.String(url=graphene.String(required=True))

    #  @login_required
    def resolve_url_shortner(self, info, **kwargs):
        if info.context.user.is_authenticated:
            url = kwargs['url']
            shorted = UrlMap.objects.filter(full_url=url).first()
            if shorted:
                return shorted.short_url
            return shortener.create(info.context.user, kwargs['url'])
        return ''
