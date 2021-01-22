import json
from datetime import datetime

from django.views import View
from django.http import JsonResponse
from django.db.models import Prefetch, Q, F

from user.models import User
from .models import Question
from .models import QuestionType
from .models import AnswerStatus
from product.models import Product
from user.utils import login_decorator


class QuestionView(View):
    @login_decorator
    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 100000000000))
            offset = int(request.GET.get('offset', 0))

            product_id = request.GET.get('product', None)

            questions = Question.objects.filter(product_id=product_id)
            result = [
                {
                    'number': question.id,
                    'question_type': question.question_type.id,
                    'answer_status': question.answer_status.id,
                    'title': question.title,
                    'content': question.content,
                    'question_man': question.user.username_id,
                    'created_at': question.created_at
                } for question in questions[offset:offset + limit]
            ]

            return JsonResponse({'data': result}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KeyError'}, status=400)


class QuestionDetailView(View):
    @login_decorator
    def get(self, request, user_id, question_id):
        try:
            user = User.objects.get(id=user_id)
            question = Question.objects.get(id=question_id)

            result = {
                'question_type': question.question_type.id,
                'product_name': question.product.name,
                'name': user.name,
                'email': user.email_address,
                'phone_number': user.phone_number,
                'title': question.title,
                'content': question.content
            }

            return JsonResponse({"result": result}, status=200)

        except Question.DoesNotExist:
            return JsonResponse({'message': 'INVALID_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=200)

    @login_decorator
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            type_id = data['type_id']
            answer_status_id = data['answer']
            product_id = data['product_name']
            title = data['title']
            content = data['content']

            Question.objects.create(
                user_id=user_id,
                product_id=product_id,
                title=title,
                content=content,
                question_type_id=type_id,
                answer_status=answer_status_id,
            )

            return JsonResponse({'message': 'success'}, status=200)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=200)

    # def put(self, request, user_id):


class QuestionInfoView(View):
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        login_user = User.objects.get(id=request.user)
        product_name = Product.objects.get(name=data['product_name'])
        return JsonResponse(
            {'name': login_user.name, 'email': login_user.email_address, 'phone_number': login_user.phone_number,
             'product_name': product_name.name}, status=200)


class QuestionEnrollView(View):
    @login_decorator
    def post(self, request):
        try:
            data = json.loads(request.body)
            login_user = User.objects.get(id=request.user)
            quest_type = QuestionType.objects.get(id=data["type"])
            answer = AnswerStatus.objects.get(id=data["answer"])
            product_name = Product.objects.get(name=data["product_name"])
            Question.objects.create(user=login_user,
                                    product=product_name,
                                    title=data["title"],
                                    content=data["content"],
                                    question_type=quest_type,
                                    answer_status=answer,
                                    created_at=datetime.now(), )
            return JsonResponse({'message': 'success'}, status=200)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=200)


class QuestionModifyView(View):
    @login_decorator
    def delete(self, request, question_number):
        try:
            question_delete = Question.objects.get(id=question_number)
            question_delete.delete()
            return JsonResponse({'message': 'success'}, status=200)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=200)

    @login_decorator
    def get(self, request, question_number):
        try:
            login_user = User.objects.get(id=request.user)
            question = Question.objects.get(id=question_number)
            return JsonResponse({'question_type': question.question_type.id,
                                 'product_name': question.product.name,
                                 'name': login_user.name,
                                 'email': login_user.email_address,
                                 'phone_number': login_user.phone_number,
                                 'title': question.title,
                                 'content': question.content}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=200)

    @login_decorator
    def put(self, request, question_number):
        try:
            data = json.loads(request.body)
            login_user = User.objects.get(id=request.user)
            question_type = QuestionType.objects.get(id=data['update_question_type'])
            quesiton_type_update = Question.objects.filter(id=question_number).update(question_type=question_type,
                                                                                      title=data[
                                                                                          'update_question_title'],
                                                                                      content=data[
                                                                                          'update_question_content'])

            return JsonResponse({'message': 'success'}, status=200)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
