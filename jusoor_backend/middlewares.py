from django.utils import timezone
from django.core.cache import cache


def update_last_visited(get_response):


    def middleware(request):
        response = get_response(request)
        if request.user.is_authenticated and cache.get(f'last_seen_{request.user.id}', default=None) == None:
                request.user.last_activity = timezone.now()
                request.user.save()
                cache.set(f'last_seen_{request.user.id}', timezone.now())
        return response

    return middleware