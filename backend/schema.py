import graphene
from graphene.contrib.django.debug import DjangoDebugMiddleware

from .schema_queries import Query
from .schema_mutations import Mutation

schema = graphene.Schema(
    name="Naturebismo's Relay Schema",
    middlewares=[DjangoDebugMiddleware()]
)

schema.query = Query
schema.mutation = Mutation
