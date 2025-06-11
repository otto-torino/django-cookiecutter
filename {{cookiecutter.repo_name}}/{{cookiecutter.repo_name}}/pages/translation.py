from modeltranslation.translator import AlreadyRegistered, TranslationOptions, register

from .models import (
    Page,
    PageContent,
    PageContentBoxItem,
    PageContentBoxMenu,
    PageContentImage,
    PageContentLayout,
    PageContentLayoutItem,
    PageContentMap,
    PageContentMapItem,
    PageContentMultiImage,
    PageContentMultiImageItem,
    PageContentRssFeed,
    PageContentText,
    PageContentTextImage,
    PageContentVideo,
    # PageContentTransport,
)

# PageContent is the used by other apps when extending pages app to add other content blocks. See PageContentAttachment from cabinet
# Other apps need to register PageContent for translation before content blocks, so we need to use try/except to avoid AlreadyRegistered error
try:

    @register(PageContent)
    class PageContentTranslationOptions(TranslationOptions):
        fields = ("name",)

except AlreadyRegistered:
    pass


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(PageContentText)
class PageContentTextTranslationOptions(TranslationOptions):
    fields = ("content",)


@register(PageContentImage)
class PageContentImageTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(PageContentTextImage)
class PageContentTextImageTranslationOptions(TranslationOptions):
    fields = ("text",'caption',)


@register(PageContentMultiImage)
class PageContentMultiImageTranslationOptions(TranslationOptions):
    pass


@register(PageContentMultiImageItem)
class PageContentMultiImageItemTranslationOptions(TranslationOptions):
    fields = ("caption",)


@register(PageContentBoxMenu)
class PageContentBoxMenuTranslationOptions(TranslationOptions):
    pass


@register(PageContentBoxItem)
class PageContentBoxItemTranslationOptions(TranslationOptions):
    fields = ("name", "icon_text", )


@register(PageContentRssFeed)
class PageContentRssFeedTranslationOptions(TranslationOptions):
    pass


@register(PageContentMap)
class PageContentMapTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(PageContentMapItem)
class PageContentMapItemTranslationOptions(TranslationOptions):
    fields = ("name", "caption")


@register(PageContentVideo)
class PageContentVideoTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(PageContentLayout)
class PageContentLayoutTranslationOptions(TranslationOptions):
    fields = ()

@register(PageContentLayoutItem)
class PageContentLayoutItemTranslationOptions(TranslationOptions):
    fields = ('text', )

# @register(PageContentTransport)
# class PageContentTransportTranslationOptions(TranslationOptions):
#     pass
