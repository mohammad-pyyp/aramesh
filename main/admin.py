from django.contrib import admin
# from .models import Reserve
from django.contrib.auth.models import Group

admin.site.unregister(Group)


# class ReserveAdmin(admin.ModelAdmin):
#     list_display = ('first_name','last_name','phone_number','created_at', "abjad") 
    
    

# admin.site.register(Reserve, ReserveAdmin)