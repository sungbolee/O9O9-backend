import json
import re
import bcrypt
import jwt
import requests

from django.http import JsonResponse
from django.views import View
from django.db.models import Q

from .models import User
from my_settings import SECRET, ALGORITHM

from util.utils import (
    name_validation,
    email_validation,
    password_validation,
    login_decorator
)


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            username_id  = data['ID']
            name         = data['name']
            email        = data['email']
            password     = data['password']
            phone_number = data['phone_number']

            if User.objects.filter(Q(email_address=email) | Q(phone_number=phone_number)).exists():
                return JsonResponse({'message': 'EXISTING_ACCOUNT'}, status=400)

            if not name_validation(name):
                return JsonResponse({'message': 'INVALID_NAME'}, status=401)

            if not email_validation(email):
                return JsonResponse({'message': 'INVALID_EMAIL'}, status=401)

            if not password_validation(password):
                return JsonResponse({'message': 'INVALID_PASSWORD'}, status=401)

            User.objects.create(
                username_id  = username_id,
                password     = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                name         = name,
                phone_number = phone_number,
                email_address= email
            )

            return JsonResponse({'message': 'SUCCESS'}, status=200)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)


class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            user     = User.objects.get(email_address=data['email'])
            password = data['password']

            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({"MESSAGE": "INVALID_PASSWORD"}, status=401)

            token = jwt.encode({'user_id': user.id}, SECRET, ALGORITHM).decode('utf-8')

            return JsonResponse({'token': token}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'message': "NO_EXIST_USER"}, status=401)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR:{e}'}, status=400)


class KakaoSignInView(View):
    def post(self, request):
        try:
            access_token = request.headers.get('Authorization', None)

            if not access_token:
                return JsonResponse({'MESSAGE': 'TOKEN_REQUIRED'}, status=400)

            response = requests.get('https://kapi.kakao.com/v2/user/me', headers={'Authorization': 'Bearer ' + access_token}).json()

            if 'email' not in response['kakao_account']:
                return JsonResponse({'MESSAGE': 'EMAIL_REQUIRED'}, status=405)

            kakao_user = User.objects.get_or_create(
                username_id   = response["properties"]["nickname"],
                email_address = response["kakao_account"]["email"]
            )[0]
            token = jwt.encode({'user_id': kakao_user.id}, SECRET, ALGORITHM).decode('UTF-8')

            return JsonResponse({'access_token': token}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'message': 'INVALID_ERROR'}, status=400)
        except KeyError as e:
            return JsonResponse({'message': f'KEY_ERROR{e}'}, status=400)
