import uuid

from django.db import models


class Musik(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    judul = models.CharField(max_length=100)
    genre = models.CharField(max_length=100, blank=True, null=True)
    penyanyi = models.CharField(max_length=100)
    produser = models.CharField(max_length=100, blank=True, null=True)
    arranger = models.CharField(max_length=100, blank=True, null=True)
    lokasi = models.CharField(max_length=100, blank=True, null=True)
    bahasa = models.CharField(max_length=100, blank=True, null=True)
    beat = models.CharField(max_length=100, blank=True, null=True)
    style = models.CharField(max_length=100, blank=True, null=True)
    mood = models.CharField(max_length=100, blank=True, null=True)

    media = models.CharField(max_length=100, blank=True, null=True)
    tahun = models.IntegerField(blank=True, null=True)
    durasi = models.FloatField()

    # Sumber file musik di Azure Blob Storage (matches "path" in your kamus data)
    path = models.URLField(max_length=255, blank=True, default='')

    def __str__(self) -> str:
        return f"{self.judul} - {self.penyanyi}"
