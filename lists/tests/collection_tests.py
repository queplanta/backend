from backend.tests import UserTestCase
from graphql_relay.node.node import to_global_id

from life.tests.factories import LifeNodeFactory
from lists.models import CollectionItem, WishItem
from .factories import CollectionItemFactory, WishItemFactory


class CollectionListTest(UserTestCase):
    def test_users_collection_list(self):
        self._do_login()
        life_node = LifeNodeFactory()

        CollectionItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        CollectionItemFactory(
            plant=life_node.document,
            user=self.user_2.document,
        )
        response = self.graphql({
            'query': '''
                query UserCollectionQuery($id: ID!) {
                    user(id: $id) {
                        idInt
                        collectionList(first: 10) {
                            totalCount
                            edges {
                                node {
                                    id
                                    plant {
                                        id
                                        title
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': to_global_id("User", self.user.document.pk),
            },
        }, client=self.client)

        collection_list_length = response.json()['data']['user']['collectionList']['totalCount']
        self.assertEqual(collection_list_length, 1)

    def test_life_node_collection_list(self):
        self._do_login()
        life_node = LifeNodeFactory()
        life_node_2 = LifeNodeFactory()

        CollectionItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        CollectionItemFactory(
            plant=life_node.document,
            user=self.user_2.document,
        )
        CollectionItemFactory(
            plant=life_node_2.document,
            user=self.user.document,
        )
        response = self.graphql({
            'query': '''
                query Q($id: ID!) {
                    lifeNode(id: $id) {
                        collectionList(first: 10) {
                            totalCount
                            edges {
                                node {
                                    id
                                    user {
                                        username
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': to_global_id("LifeNode", life_node.document.pk),
            },
        }, client=self.client)

        collection_list_length = response.json()['data']['lifeNode']['collectionList']['totalCount']
        self.assertEqual(collection_list_length, 2)

    def test_mutation_add(self):
        self._do_login()
        life_node = LifeNodeFactory()
        plant_id = to_global_id("LifeNode", life_node.document.pk)

        response = self.graphql({
            'query': '''
                mutation M($input_0: CollectionItemAddInput!) {
                    collectionItemAdd(input: $input_0) {
                        clientMutationId
                        collectionItem {
                            node {
                                plant {
                                    id
                                }
                            }
                        }
                        errors {
                            code
                        }
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'plantId': plant_id
                }
            }
        }, client=self.client)

        expected = {
            'data': {
                'collectionItemAdd': {
                    'collectionItem': {
                        'node': {
                            'plant': {
                                'id': plant_id,
                            },
                        },
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_mutation_delete(self):
        self._do_login()
        life_node = LifeNodeFactory()
        collection_item = CollectionItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        collection_item_id = to_global_id("CollectionItem", collection_item.document.pk)

        response = self.graphql({
            'query': '''
                mutation M($input_0: CollectionItemDeleteInput!) {
                    collectionItemDelete(input: $input_0) {
                        clientMutationId
                        deletedId
                        errors {
                            code
                        }
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'id': collection_item_id
                }
            }
        }, client=self.client)

        expected = {
            'data': {
                'collectionItemDelete': {
                    'deletedId': collection_item_id,
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)
        self.assertEqual(CollectionItem.objects.filter(user=self.user.document).count(), 0)


class WishListTest(UserTestCase):
    def test_users_wish_list(self):
        self._do_login()
        life_node = LifeNodeFactory()

        CollectionItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        CollectionItemFactory(
            plant=life_node.document,
            user=self.user_2.document,
        )
        response = self.graphql({
            'query': '''
                query UserCollectionQuery($id: ID!) {
                    me {
                        id
                        username
                    }
                    user(id: $id) {
                        id
                        idInt
                        collectionList(first: 10) {
                            totalCount
                            edges {
                                node {
                                    id
                                    plant {
                                        id
                                        title
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': to_global_id("User", self.user.document.pk),
            },
        }, client=self.client)

        collection_list_length = response.json()['data']['user']['collectionList']['totalCount']
        self.assertEqual(collection_list_length, 1)

    def test_life_node_wish_list(self):
        self._do_login()
        life_node = LifeNodeFactory()
        life_node_2 = LifeNodeFactory()

        WishItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        WishItemFactory(
            plant=life_node.document,
            user=self.user_2.document,
        )
        WishItemFactory(
            plant=life_node_2.document,
            user=self.user.document,
        )
        response = self.graphql({
            'query': '''
                query Q($id: ID!) {
                    lifeNode(id: $id) {
                        wishList(first: 10) {
                            totalCount
                            edges {
                                node {
                                    id
                                    user {
                                        username
                                    }
                                }
                            }
                        }
                    }
                }
                ''',
            'variables': {
                'id': to_global_id("LifeNode", life_node.document.pk),
            },
        }, client=self.client)

        collection_list_length = response.json()['data']['lifeNode']['wishList']['totalCount']
        self.assertEqual(collection_list_length, 2)

    def test_mutation_add(self):
        self._do_login()
        life_node = LifeNodeFactory()
        plant_id = to_global_id("LifeNode", life_node.document.pk)

        response = self.graphql({
            'query': '''
                mutation M($input_0: WishItemAddInput!) {
                    wishItemAdd(input: $input_0) {
                        clientMutationId
                        wishItem {
                            node {
                                plant {
                                    id
                                }
                            }
                        }
                        errors {
                            code
                        }
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'plantId': plant_id
                }
            }
        }, client=self.client)

        expected = {
            'data': {
                'wishItemAdd': {
                    'wishItem': {
                        'node': {
                            'plant': {
                                'id': plant_id,
                            },
                        },
                    },
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_mutation_delete(self):
        self._do_login()
        life_node = LifeNodeFactory()
        wish_item = WishItemFactory(
            plant=life_node.document,
            user=self.user.document,
        )
        wish_item_id = to_global_id("WishItem", wish_item.document.pk)

        response = self.graphql({
            'query': '''
                mutation M($input_0: WishItemDeleteInput!) {
                    wishItemDelete(input: $input_0) {
                        clientMutationId
                        deletedId
                        errors {
                            code
                        }
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'id': wish_item_id
                }
            }
        }, client=self.client)

        expected = {
            'data': {
                'wishItemDelete': {
                    'deletedId': wish_item_id,
                    'clientMutationId': '1',
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)
        self.assertEqual(WishItem.objects.filter(user=self.user.document).count(), 0)
