import re

from django.core.exceptions import ValidationError


class RegexPasswordValidator:
    regex = r"^(?=(?:[^A-Z]*[A-Z]){2})\S{7,}$"
    message = (
        "La contraseña debe tener al menos 7 caracteres sin espacios "
        "y contener al menos 2 letras mayúsculas."
    )
    code = "password_invalid_format"

    def validate(self, password, user=None):
        if not re.match(self.regex, password):
            raise ValidationError(self.message, code=self.code)

    def get_help_text(self):
        return self.message