from modeltranslation.translator import TranslationOptions, register

# Register attachment content block for translation if pages app is installed
try:
    from .models import AttachmentModel, PageContentMultiAttachment

    @register(AttachmentModel)
    class AttachmentModelTranslationOptions(TranslationOptions):
        fields = ("name", "description")

    @register(PageContentMultiAttachment)
    class PageContentMultiAttachmentTranslationOptions(TranslationOptions):
        pass
except:
    pass
