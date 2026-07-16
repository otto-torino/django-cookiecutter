from baton.views import CreateTagsView


class TagallCreateTagsView(CreateTagsView):
    def set_tag_label(self, item, label_field, label):
        field_names = [field.name for field in item._meta.fields]
        language_code = self.get_default_language().split("-")[0]
        localized_field = f"{label_field}_{language_code}"

        if label_field in field_names:
            item.__dict__[label_field] = label

        if localized_field in field_names:
            setattr(item, localized_field, label)
