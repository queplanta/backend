from backend.tests import UserTestCase

from django.contrib.gis.geos import Point
from .factories import OccurrenceFactory


class OccurrenceClusterTest(UserTestCase):
    def test_filter_within(self):
        OccurrenceFactory(location=Point(-19.943256710511975, -43.98101806640725))
        OccurrenceFactory()
        OccurrenceFactory()

        response = self.graphql({
            'query': '''
                query M($bbox: String!) {
                    allOccurrencesCluster(withinBbox: $bbox) {
                        count
                        polygon
                    }
                }
            ''',
            'variables': {
                'bbox': '-19.943256710511875,-43.98101806640625,-19.90290981124127,-43.88660430908203'
            },
        })
        
        result = response.json()['data']

        self.assertEqual(len(result['allOccurrencesCluster']), 1)
        self.assertEqual(result['allOccurrencesCluster'][0]['count'], 2)
