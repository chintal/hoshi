

class TranslatableStructuredMessage(object):
    def __init__(self, parts: dict):
        self._templates = {}
        self._parts = parts

    def install_template(self, language, template):
        if language in self._templates.keys():
            self._templates[language].append(template)
        else:
            self._templates[language] = [template]

    def translated(self, translate, context):
        parts = {k: translate(context, v) for k, v in self._parts.items()}
        for template in self._templates[context['language']]:
            try:
                return template.format(**parts)
            except KeyError:
                continue
        raise KeyError
