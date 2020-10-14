from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    ListStats = apps.get_model("lists", "ListStats")
    CollectionItem = apps.get_model("lists", "CollectionItem")
    WishItem = apps.get_model("lists", "WishItem")
    for user in User.objects.filter(is_tip=True, document__deleted_at__isnull=True):
        stats, created = ListStats.objects.get_or_create(
            document=user.document
        )
        stats.collection_count = CollectionItem.objects_revisions.filter(user=user.document, is_tip=True, document__deleted_at__isnull=True).count()
        stats.wish_count = WishItem.objects_revisions.filter(user=user.document, is_tip=True, document__deleted_at__isnull=True).count()
        stats.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0006_liststats'),
    ]

    operations = [
        migrations.RunPython(forwards_func)
    ]
