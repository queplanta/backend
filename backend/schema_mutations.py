import graphene

from accounts.mutations import Mutations as AccountsMutations
from posts import mutations as posts_mutations
from tags.mutations import TagCreate, TagEdit, TagDelete
from commenting.mutations import CommentCreate, CommentEdit, CommentDelete
from voting import mutations as voting_mutations
from db import mutations as db_mutations
from life.mutations import Mutations as LifeMutations
from occurrences import mutations as occurrences_mutations
from pages import mutations as page_mutations
from lists.mutations import Mutations as ListsMutations
from images.mutations import Mutations as ImagesMutations


def m_field(m):
    return m.Field()


class Mutation(AccountsMutations, ImagesMutations, LifeMutations, ListsMutations, graphene.ObjectType):
    postCreate = m_field(posts_mutations.PostCreate)
    postEdit = m_field(posts_mutations.PostEdit)
    postDelete = m_field(posts_mutations.PostDelete)

    pageCreate = m_field(page_mutations.PageCreate)
    pageEdit = m_field(page_mutations.PageEdit)
    pageDelete = m_field(page_mutations.PageDelete)

    tagCreate = m_field(TagCreate)
    tagEdit = m_field(TagEdit)
    tagDelete = m_field(TagDelete)

    commentCreate = m_field(CommentCreate)
    commentEdit = m_field(CommentEdit)
    commentDelete = m_field(CommentDelete)

    voteSet = m_field(voting_mutations.VoteSet)
    voteDelete = m_field(voting_mutations.VoteDelete)

    occurrenceCreate = m_field(occurrences_mutations.OccurrenceCreate)
    occurrenceDelete = m_field(occurrences_mutations.OccurrenceDelete)
    whatIsThisCreate = m_field(occurrences_mutations.WhatIsThisCreate)
    whatIsThisIdentify = m_field(occurrences_mutations.WhatIsThisIdentify)

    suggestionIDCreate = m_field(occurrences_mutations.SuggestionIDCreate)
    suggestionIDDelete = m_field(occurrences_mutations.SuggestionIDDelete)

    revisionRevert = m_field(db_mutations.RevisionRevert)
