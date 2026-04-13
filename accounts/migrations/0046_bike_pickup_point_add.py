
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0045_alter_tour_booking_add_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='bike',
            name='pickup_location',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='bike',
            name='pickup_location_latitude',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='bike',
            name='pickup_location_longitude',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True),
        ),
    ]
