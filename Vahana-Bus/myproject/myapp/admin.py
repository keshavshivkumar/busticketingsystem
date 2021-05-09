from django.contrib import admin
from .models import Bus, User, Book, Operator

# Register your models here.

admin.site.register(Bus)
admin.site.register(User)
admin.site.register(Book)
admin.site.register(Operator)


