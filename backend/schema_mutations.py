import graphene

from accounts import mutations as accounts_mutations
from posts.mutations import PostCreate, PostEdit, PostDelete
from tags.mutations import TagCreate, TagEdit, TagDelete
from commenting.mutations import CommentCreate, CommentEdit, CommentDelete
from voting import mutations as voting_mutations
from db import mutations as db_mutations
from life import mutations as life_mutations


class Mutation(graphene.ObjectType):
    register = graphene.Field(accounts_mutations.Register)
    registerAndAuthenticate = graphene.Field(
        accounts_mutations.RegisterAndAuthenticate)
    authenticate = graphene.Field(accounts_mutations.Authenticate)
    deauthenticate = graphene.Field(accounts_mutations.Deauthenticate)
    mePasswordChange = graphene.Field(accounts_mutations.PasswordChange)
    mePasswordResetEmail = graphene.Field(
        accounts_mutations.PasswordResetEmail)
    mePasswordResetComplete = graphene.Field(
        accounts_mutations.PasswordResetComplete)
    meProfileEdit = graphene.Field(
        accounts_mutations.ProfileEdit)
    meProfileChangeAvatar = graphene.Field(
        accounts_mutations.ProfileChangeAvatar)

    postCreate = graphene.Field(PostCreate)
    postEdit = graphene.Field(PostEdit)
    postDelete = graphene.Field(PostDelete)

    tagCreate = graphene.Field(TagCreate)
    tagEdit = graphene.Field(TagEdit)
    tagDelete = graphene.Field(TagDelete)

    commentCreate = graphene.Field(CommentCreate)
    commentEdit = graphene.Field(CommentEdit)
    commentDelete = graphene.Field(CommentDelete)

    voteSet = graphene.Field(voting_mutations.VoteSet)
    voteDelete = graphene.Field(voting_mutations.VoteDelete)

    lifeNodeCreate = graphene.Field(life_mutations.LifeNodeCreate)
    lifeNodeEdit = graphene.Field(life_mutations.LifeNodeEdit)
    lifeNodeDelete = graphene.Field(life_mutations.LifeNodeDelete)

    revisionRevert = graphene.Field(db_mutations.RevisionRevert)
