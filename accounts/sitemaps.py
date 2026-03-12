from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Tour, BlogPost, Page, Category, City, Country, DestinationRegion

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return [
            'home', 
            'tour_list_fronted', 
            'find_tour', 
            'tour_providers_fronted',
            'tour_countries_fronted',
            'tour_cities_fronted',
            'tour_destination_regions_fronted',
            'blog_list_fronted',
            'contactus',
            'testimonial',
            'rent_bike',
            'souvenirs_list_frontend',
        ]

    def location(self, item):
        return reverse(item)

class TourSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Tour.objects.filter(status='active')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('tour_detail', args=[obj.id])

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog_detail_fronted', args=[obj.id])

class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Page.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('page_view_fronted', args=[obj.id, obj.slug])

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(status='active')

    def location(self, obj):
        return reverse('tour_list_fronted') + f'?category={obj.id}'

class CitySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return City.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('tour_list_fronted') + f'?city={obj.id}'

class CountrySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Country.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('tour_list_fronted') + f'?country={obj.id}'

class DestinationRegionSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return DestinationRegion.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('tour_list_fronted') + f'?region={obj.id}'
