from pathlib import Path

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from PIL import Image

from .models import Folder, get_file_model


ALLOWED_EDITOR_JS_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def _is_valid_image(uploaded_file):
    if uploaded_file.content_type not in ALLOWED_EDITOR_JS_IMAGE_TYPES:
        return False

    try:
        Image.open(uploaded_file).verify()
    except Exception:
        return False
    finally:
        uploaded_file.seek(0)

    return True


@require_POST
@staff_member_required
def editor_js_image_upload(request):
    image = request.FILES.get("image")
    if not image:
        return JsonResponse(
            {"success": 0, "message": _("No image file provided.")},
            status=400,
        )

    if not _is_valid_image(image):
        return JsonResponse(
            {"success": 0, "message": _("Invalid image file.")},
            status=400,
        )

    folder, _created = Folder.objects.get_or_create(parent=None, name="Editor.js")
    file_model = get_file_model()
    cabinet_file = file_model(
        folder=folder,
        image_file=image,
        image_alt_text=Path(image.name).stem.replace("_", " ").replace("-", " ")[:1000],
    )
    cabinet_file.save()

    return JsonResponse(
        {
            "success": 1,
            "file": {
                "url": cabinet_file.image_file.url,
            },
        }
    )


def permalink(request, file_id):
    file = get_object_or_404(get_file_model(), pk=file_id)
    return redirect(file.file.url)
