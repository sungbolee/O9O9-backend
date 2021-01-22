import jwt

from django.http import JsonResponse

from my_settings import SECRET, ALGORITHM
from user.models import User


def login_decorator(login_required=False):
    def real_decorator(func):
        def wrapper(self, request, *args, **kwargs):
            try:
                access_token = request.headers.get('Authorization')

                if not login_required:
                    request.user = User.objects.none()
                    return func(self, request, *args, **kwargs)

                payload = jwt.decode(access_token, SECRET, algorithm=ALGORITHM)

                request.user = User.objects.get(id=payload['user_id'])

                return func(self, request, *args, **kwargs)

            except jwt.DecodeError:
                return JsonResponse({'message': 'UNAUTHORIZED'}, status=401)

            except User.DoesNotExist:
                return JsonResponse({'message': 'INVALID_USER'}, status=401)

        return wrapper
    return real_decorator
