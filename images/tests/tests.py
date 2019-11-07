import os
from django.test.client import MULTIPART_CONTENT
from backend.tests import UserTestCase
from pages.tests.factories import PageFactory
from graphql_relay.node.node import to_global_id

from .factories import ImageFactory

dir_path = os.path.dirname(os.path.realpath(__file__))

class ImageTest(UserTestCase):
    def test_cant_create_images_without_perm(self):
        self._do_login()
        page = PageFactory()
        with open(f"{dir_path}/image-example.jpg", "rb") as fp:
            response = self.graphql({
                'query': '''
                    mutation M($input_0: ImageCreateInput!) {
                        imageCreate(input: $input_0) {
                            clientMutationId,
                            errors {
                                code,
                            },
                        }
                    }
                    ''',
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'parent': to_global_id("Page", page.document.pk),
                        'description': 'image description'
                    }
                },
                'image': fp,
            }, client=self.client, content_type=MULTIPART_CONTENT)
        expected = {
            'data': {
                'imageCreate': {
                    'clientMutationId': '1',
                    'errors': [{
                        'code': 'permission_required'
                    }]
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_admin_create_image(self):
        self._do_login_admin()
        page = PageFactory()
        with open(f"{dir_path}/image-example.jpg", "rb") as fp:
            response = self.graphql({
                'query': '''
                    mutation M($input_0: ImageCreateInput!) {
                        imageCreate(input: $input_0) {
                            clientMutationId,
                            image {
                                node {
                                    description
                                }
                            }
                            errors {
                                code,
                            },
                        }
                    }
                    ''',
                'variables': {
                    'input_0': {
                        'clientMutationId': '1',
                        'parent': to_global_id("Page", page.document.pk),
                        'description': 'image description'
                    }
                },
                'image': fp,
            }, client=self.client, content_type=MULTIPART_CONTENT)
        expected = {
            'data': {
                'imageCreate': {
                    'image': {
                        'node': {
                            'description': 'image description'
                        }
                    },
                    'clientMutationId': '1',
                    'errors': []
                },
            }
        }
        self.assertEqual(response.json(), expected)

    def test_admin_delete_image(self):
        self._do_login_admin()
        image = ImageFactory()
        id_to_delete = to_global_id("Image", image.document.pk)
        response = self.graphql({
            'query': '''
                mutation M($input_0: ImageDeleteInput!) {
                    imageDelete(input: $input_0) {
                        clientMutationId,
                        imageDeletedID,
                        errors {
                            code,
                        },
                    }
                }
                ''',
            'variables': {
                'input_0': {
                    'clientMutationId': '1',
                    'id': id_to_delete,
                }
            },
        }, client=self.client)
        expected = {
            'data': {
                'imageDelete': {
                    'clientMutationId': '1',
                    'imageDeletedID': id_to_delete,
                    'errors': None
                },
            }
        }
        self.assertEqual(response.json(), expected)
