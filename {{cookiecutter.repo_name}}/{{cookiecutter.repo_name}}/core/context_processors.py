from django.conf import settings


def debug(request):
    return {'DEBUG': settings.DEBUG}


def absurl(request):
    return {'ABSURL': request.build_absolute_uri()}


def cookierulez(request):
    return {'COOKIERULEZ_WIDGET_CODE': settings.COOKIERULEZ_WIDGET_CODE}
