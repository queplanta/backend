import graphene

from .schema_queries import Query
from .schema_mutations import Mutation

schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)
