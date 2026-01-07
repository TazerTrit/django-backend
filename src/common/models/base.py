from datetime import timezone

from django.db import models

from src.common.utils.time import get_elapsed_time_with_message

from django.utils import timezone

from datetime import datetime

def get_default_now():
    return timezone.now()


class TimedBaseModel(models.Model):
    created_at = models.DateTimeField(
        default=datetime.now,  # ← менять во время миграций
        editable=False
    )
    updated_at = models.DateTimeField(
        default=datetime.now,  # менять во время миграций
        editable=False
    )

    class Meta:
        abstract = True

    def time_elapsed_since_creation(self) -> tuple[int, str, str]:
        """
        Returns the elapsed time since creation,
        in tuple[int, str, str]:
            int - the elapsed time
            str - time unit
            str - message
        see utility 'get_elapsed_time_with_message'
        """
        now = timezone.now()
        elapsed_time = now - self.created_at
        # Determine time unit based on elapsed time
        return get_elapsed_time_with_message(elapsed_time)
