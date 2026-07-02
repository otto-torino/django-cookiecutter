from modeltranslation.translator import AlreadyRegistered, TranslationOptions, register

# Register attachment content block for translation if pages app is installed
try:
    from pages.models import PageContent

    from .models import AttachmentModel, PageContentMultiAttachment

    try:

        @register(PageContent)
        class PageContentTranslationOptions(TranslationOptions):
            fields = ("name",)

    except AlreadyRegistered:
        pass

    @register(AttachmentModel)
    class AttachmentModelTranslationOptions(TranslationOptions):
        fields = ("name", "description")

    @register(PageContentMultiAttachment)
    class PageContentMultiAttachmentTranslationOptions(TranslationOptions):
        pass
except:
    pass
