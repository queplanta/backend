from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve as static_serve

from graphene_django.views import GraphQLView
from .schema import schema


def dumb_view(request, *args, **kwargs):
    return None

URL_PASSWORD_RESET = r'me/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/'


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(schema=schema,
                                                     graphiql=True))),

    url(r'^%s$' % URL_PASSWORD_RESET,
        dumb_view, name='password_reset_confirm'),

    url(r'^public/(?P<path>.*)$', static_serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^static/(?P<path>.*)$', static_serve,
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
]
