# core/context_processors/year.py
from django.utils import timezone


def year(request):
    now = timezone.now()
    return {'year': now.year}
