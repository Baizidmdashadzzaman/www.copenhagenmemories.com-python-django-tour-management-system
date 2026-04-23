
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0047_add_seo_filed_db'),
    ]

    operations = [

        migrations.AddField(
            model_name='teammember',
            name='facebook',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='teammember',
            name='twitter',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='teammember',
            name='instagram',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='teammember',
            name='linkedin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='teammember',
            name='pinterest',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),

    ]
