# queplanta's backend [![Build Status](https://travis-ci.org/queplanta/backend.svg?branch=master)](https://travis-ci.org/queplanta/backend)

Responsible for all the server-side logic on top of [Django](https://github.com/django/django) using [GraphQL](https://github.com/facebook/graphql) (through [graphene-django](https://github.com/graphql-python/graphene)) for the communication with [queplanta/frontend](https://github.com/queplanta/frontend).

Everything starts with a data revision control ([db](https://github.com/queplanta/backend/tree/master/db) module), it's the base of everything. All data is controlled by it, all changes are recorded so we have a consistent history of what happened, who did it and from where the action came from. Since all data is public, so is all of it's history, no object is ever deleted from the database.

All model's should extend from `db.models.DocumentBase` instead of `django.db.models.Model`, see [posts/models.py](https://github.com/queplanta/backend/tree/master/db/models.py) as an example.

The key difference from django's Model is that you *should* always pass `request` as the first argument to `save` and `delete` methods.

It needs the request instance to store the authenticated user, the useragent and it's ip address so we can better audit changes in the future.

`DucumentBase.objects` uses a custom manager that always returns the document's current state, to search on history use `objects_revisions` instead, like:

```python
>>> post = Post(body='some value')
>>> post.save(request=request)
>>> print(Post.objects.all().count())
1
>>> print(Post.objects_revisions.all().count())
1
>>> post.body = 'edited'
>>> post.save(request=request)
>>> print(Post.objects.all().count())
1
>>> print(Post.objects_revisions.all().count())
2
>>> post.delete(request=request)
>>> print(Post.objects.all().count())
0
>>> print(Post.objects_revisions.all().count())
3
```

To contribute to the project please go to [CONTRIBUTING.md](https://github.com/queplanta/frontend/blob/master/CONTRIBUTING.md)
