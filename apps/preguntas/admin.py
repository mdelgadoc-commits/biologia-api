from django.contrib import admin
from .models import Pregunta, ElementoPregunta, PreguntaAbierta


class ElementoPreguntaInline(admin.TabularInline):
    model = ElementoPregunta
    extra = 1


class PreguntaAdmin(admin.ModelAdmin):
    list_display = ["id", "tema", "tipo", "dificultad", "activa"]
    list_filter = ["tema", "tipo", "activa"]
    inlines = [ElementoPreguntaInline]


admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(PreguntaAbierta)
