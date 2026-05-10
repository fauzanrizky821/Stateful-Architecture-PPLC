from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .azure_blob import build_blob_sas_url, delete_blob
from .forms import MusikUploadForm
from .models import Musik


def upload_musik(request):
    message = ''

    if request.method == 'POST':
        form = MusikUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                return redirect('library_musik')
            except Exception as exc:
                message = f'Gagal upload ke Azure Blob Storage: {exc}'
    else:
        form = MusikUploadForm()

    return render(request, 'musik/upload.html', {'form': form, 'message': message})


def library_musik(request):
    musics = Musik.objects.exclude(path='').order_by('judul')
    for music in musics:
        try:
            music.playback_url = build_blob_sas_url(music.path)
        except Exception:
            music.playback_url = music.path
    return render(request, 'musik/library.html', {'musics': musics})


@require_POST
@csrf_protect
def delete_musik(request, musik_id):
    """Delete musik dan file nya dari Blob Storage."""
    try:
        musik = Musik.objects.get(id=musik_id)
        
        # Delete file dari Azure Blob Storage
        if musik.path:
            delete_blob(musik.path)
        
        # Delete database record
        musik.delete()
        
        return redirect('library_musik')
    except Musik.DoesNotExist:
        return redirect('library_musik')
    except Exception as exc:
        # Redirect dengan error message
        return render(request, 'musik/library.html', {
            'error': f'Gagal menghapus musik: {exc}'
        })
