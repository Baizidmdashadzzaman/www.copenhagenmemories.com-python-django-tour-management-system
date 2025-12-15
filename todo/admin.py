from django.contrib import admin

# Register your models here.
# from .models import Todo
# admin.site.register(Todo)

from .models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    # 1. Fields to display on the change list page
    list_display = ('title', 'completed') 

    # 2. Add filters to the sidebar
    list_filter = ('title','completed')

    # 3. Add a search bar to filter by these fields
    search_fields = ('title', 'description')

    # 4. Make the fields editable directly from the list page
    list_editable = ('completed',)

    # 5. Define the order of fields on the detail page
    fields = ('title', 'description', 'completed')