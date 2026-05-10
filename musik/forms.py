import os

from django import forms

from .models import Musik
from .azure_blob import upload_mp3

try:
    from mutagen.mp3 import MP3
except Exception:  # pragma: no cover
    MP3 = None


class MusikUploadForm(forms.ModelForm):
    file_mp3 = forms.FileField(label='File MP3')

    class Meta:
        model = Musik
        fields = ['judul', 'penyanyi']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['judul'].label = 'Nama Musik'
        self.fields['penyanyi'].label = 'Penyanyi'

    def clean_file_mp3(self):
        f = self.cleaned_data.get('file_mp3')
        if not f:
            return f

        ext = os.path.splitext(getattr(f, 'name', '') or '')[1].lower()
        if ext != '.mp3':
            raise forms.ValidationError('File harus berformat .mp3')

        return f

    def save(self, commit=True):
        instance: Musik = super().save(commit=False)

        f = self.cleaned_data.get('file_mp3')
        instance.media = 'mp3'

        duration = 0.0
        if MP3 is not None and f is not None:
            try:
                # Mutagen needs a file-like object; Django UploadedFile works.
                if hasattr(f, 'seek'):
                    f.seek(0)
                audio = MP3(f)
                if audio and audio.info and audio.info.length:
                    duration = float(audio.info.length)
            except Exception:
                duration = 0.0
            finally:
                if hasattr(f, 'seek'):
                    f.seek(0)

        instance.durasi = duration

        # Upload to Azure Blob Storage and store URL in path
        if f is not None:
            # Use UUID filename to avoid collisions
            if hasattr(f, 'seek'):
                f.seek(0)
            blob_name = f"musik/{instance.id}.mp3"
            uploaded = upload_mp3(f, blob_name=blob_name)
            instance.path = uploaded.url

        if commit:
            instance.save()

        return instance
