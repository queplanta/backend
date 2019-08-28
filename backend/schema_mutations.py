import graphene

from accounts import mutations as accounts_mutations
from posts import mutations as posts_mutations
from tags.mutations import TagCreate, TagEdit, TagDelete
from commenting.mutations import CommentCreate, CommentEdit, CommentDelete
from voting import mutations as voting_mutations
from db import mutations as db_mutations
from life import mutations as life_mutations
from occurrences import mutations as occurrences_mutations
from pages import mutations as page_mutations
from lists import mutations as lists_mutations


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

    postCreate = m_field(posts_mutations.PostCreate)
    postEdit = m_field(posts_mutations.PostEdit)
    postDelete = m_field(posts_mutations.PostDelete)

    pageCreate = m_field(page_mutations.PageCreate)
    pageEdit = m_field(page_mutations.PageEdit)
    pageDelete = m_field(page_mutations.PageDelete)

    listCreate = m_field(lists_mutations.ListCreate)
    listEdit = m_field(lists_mutations.ListEdit)
    listDelete = m_field(lists_mutations.ListDelete)
    listAddItem = m_field(lists_mutations.ListAddItem)

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

    occurrenceCreate = m_field(occurrences_mutations.OccurrenceCreate)
    occurrenceDelete = m_field(occurrences_mutations.OccurrenceDelete)
    whatIsThisCreate = m_field(occurrences_mutations.WhatIsThisCreate)

    suggestionIDCreate = m_field(occurrences_mutations.SuggestionIDCreate)
    suggestionIDDelete = m_field(occurrences_mutations.SuggestionIDDelete)

    revisionRevert = m_field(db_mutations.RevisionRevert)
