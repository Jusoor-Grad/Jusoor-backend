from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class ZeroToOneDecimalField(models.DecimalField):
    """
    A custom field for storing decimals between 0 and 1 (inclusive).
    """
    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [MinValueValidator(0), MaxValueValidator(1)]
        kwargs['max_digits'] = 3
        kwargs['decimal_places'] = 2
        kwargs['blank'] = False
        kwargs['null'] = False
        super().__init__(*args, **kwargs)
