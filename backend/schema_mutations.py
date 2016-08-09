import graphene

from accounts import mutations as accounts_mutations
from posts.mutations import PostCreate, PostEdit, PostDelete
from tags.mutations import TagCreate, TagEdit, TagDelete
from commenting.mutations import CommentCreate, CommentEdit, CommentDelete
from voting import mutations as voting_mutations


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
