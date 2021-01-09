import jwt
from django.http import request,JsonResponse
from my_settings import SECRET, ALGORITHMS
from user.models import User
def check_user(func):
    def wrapper_func(self, request,**kwargs):
        for_client_token = request.headers.get('authorization')
        if for_client_token is None:
            return JsonResponse({'message': 'TOKEN PLEASE'},status=400)
        try:
            user_id = jwt.decode(for_client_token, SECRET, algorithm=ALGORITHMS)
            user = User.objects.get(id=user_id['id'])
            request.user = user.id
            return func(self,request,**kwargs)
        except KeyError:
            return JsonResponse({'message': "KEY_ERROR"}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message':'UNKNOWN_USER'},status=401)
        except jwt.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'},status=401)
    return wrapper_func