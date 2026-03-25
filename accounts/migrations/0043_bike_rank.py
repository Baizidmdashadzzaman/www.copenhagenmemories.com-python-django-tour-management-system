
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_tour_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='bike',
            name='rank',
            field=models.IntegerField(default=0),
        ),
    ]
