from django.forms import Widget

class MapWidget(Widget):
    template_name = "pages/widgets/map_widget.html"

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        return ctx
