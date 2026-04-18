
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0046_bike_pickup_point_add'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='meta_keywords',
            field=models.TextField(blank=True),
        ),
        
        migrations.AddField(
            model_name='sitesetting',
            name='home_page_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='home_page_meta_keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='home_page_meta_description',
            field=models.TextField(blank=True),
        ),

        migrations.AddField(
            model_name='sitesetting',
            name='contactus_page_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='contactus_page_meta_keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='contactus_page_meta_description',
            field=models.TextField(blank=True),
        ),

        migrations.AddField(
            model_name='sitesetting',
            name='rentbike_page_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='rentbike_page_meta_keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='rentbike_page_meta_description',
            field=models.TextField(blank=True),
        ),

        migrations.AddField(
            model_name='sitesetting',
            name='souvenirs_page_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='souvenirs_page_meta_keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='souvenirs_page_meta_description',
            field=models.TextField(blank=True),
        ),

        migrations.AddField(
            model_name='sitesetting',
            name='tours_page_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='tours_page_meta_keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='tours_page_meta_description',
            field=models.TextField(blank=True),
        ),

        migrations.AddField(
            model_name='sitesetting',
            name='blog_page_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='blog_page_meta_keywords',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='blog_page_meta_description',
            field=models.TextField(blank=True),
        ),


    ]
