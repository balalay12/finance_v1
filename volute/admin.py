from django.contrib import admin

from volute.models import Category, Many


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class ManyAdmin(admin.ModelAdmin):
    list_display = ('date', 'sum', 'category', 'comment')
    ordering = ('-date',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Many, ManyAdmin)