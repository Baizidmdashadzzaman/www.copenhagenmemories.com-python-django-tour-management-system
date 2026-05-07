
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0048_add_social_to_teammeber'),
    ]

    operations = [

        migrations.AddField(
            model_name='sitesetting',
            name='cvr_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),

    ]
