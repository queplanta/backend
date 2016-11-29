import graphene

from accounts import mutations as accounts_mutations
from posts.mutations import PostCreate, PostEdit, PostDelete
from tags.mutations import TagCreate, TagEdit, TagDelete
from commenting.mutations import CommentCreate, CommentEdit, CommentDelete
from voting import mutations as voting_mutations
from db import mutations as db_mutations
from life import mutations as life_mutations
from what import mutations as what_mutations


def m_field(m):
    return m.Field()


class Mutation(graphene.ObjectType):
    register = m_field(accounts_mutations.Register)
    registerAndAuthenticate = m_field(
        accounts_mutations.RegisterAndAuthenticate)
    authenticate = m_field(accounts_mutations.Authenticate)
    deauthenticate = m_field(accounts_mutations.Deauthenticate)
    mePasswordChange = m_field(accounts_mutations.PasswordChange)
    mePasswordResetEmail = m_field(
        accounts_mutations.PasswordResetEmail)
    mePasswordResetComplete = m_field(
        accounts_mutations.PasswordResetComplete)
    meProfileEdit = m_field(
        accounts_mutations.ProfileEdit)
    meProfileChangeAvatar = m_field(
        accounts_mutations.ProfileChangeAvatar)

    postCreate = m_field(PostCreate)
    postEdit = m_field(PostEdit)
    postDelete = m_field(PostDelete)

    tagCreate = m_field(TagCreate)
    tagEdit = m_field(TagEdit)
    tagDelete = m_field(TagDelete)

    commentCreate = m_field(CommentCreate)
    commentEdit = m_field(CommentEdit)
    commentDelete = m_field(CommentDelete)

    voteSet = m_field(voting_mutations.VoteSet)
    voteDelete = m_field(voting_mutations.VoteDelete)

    speciesCreate = m_field(life_mutations.SpeciesCreate)
    lifeNodeCreate = m_field(life_mutations.LifeNodeCreate)
    lifeNodeEdit = m_field(life_mutations.LifeNodeEdit)
    lifeNodeDelete = m_field(life_mutations.LifeNodeDelete)
    lifeNodeCharacteristicAdd = m_field(life_mutations.CharacteristicAdd)

    lifeNodeCheckQuizz = m_field(life_mutations.CheckQuizz)

    whatIsThisCreate = m_field(what_mutations.WhatIsThisCreate)
    suggestionIDCreate = m_field(what_mutations.SuggestionIDCreate)

    revisionRevert = m_field(db_mutations.RevisionRevert)
