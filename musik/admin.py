from django.contrib import admin

from .models import Musik


@admin.register(Musik)
class MusikAdmin(admin.ModelAdmin):
    list_display = ('judul', 'penyanyi', 'tahun', 'durasi')
