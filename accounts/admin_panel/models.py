from django.db import models

class DestinationRegion(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100, default='Denmark')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
