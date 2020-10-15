from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    ListStats = apps.get_model("lists", "ListStats")
    CollectionItem = apps.get_model("lists", "CollectionItem")
    WishItem = apps.get_model("lists", "WishItem")

    def update_collection(qs):
        for item in qs:
            stats, created = ListStats.objects.get_or_create(
                document=item.plant
            )
            stats.collection_count= CollectionItem.objects_revisions.filter(plant=item.plant, is_tip=True, document__deleted_at__isnull=True).count()
            stats.wish_count = WishItem.objects_revisions.filter(plant=item.plant, is_tip=True, document__deleted_at__isnull=True).count()
            stats.save()

    update_collection(CollectionItem.objects_revisions.filter(is_tip=True, document__deleted_at__isnull=True))
    update_collection(WishItem.objects_revisions.filter(is_tip=True, document__deleted_at__isnull=True))


def backwards_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0007_populate_liststats'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func)
    ]
