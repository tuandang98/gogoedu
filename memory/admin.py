from django.contrib import admin
from .models import Image, Game,Card,Player
# Register your models here.
admin.site.register(Image)
admin.site.register(Game)

admin.site.register(Player)
class CardAdmin(admin.ModelAdmin):
    list_display = ('image','game')
admin.site.register(Card,CardAdmin)