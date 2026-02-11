from django.shortcuts import get_object_or_404, redirect
from .models import File


def permalink(request, file_id):
    file = get_object_or_404(File, pk=file_id)
    return redirect(file.file.url)
