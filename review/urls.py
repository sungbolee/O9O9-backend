from django.urls import path
from .views import QuestionView, QuestionInfoView, QuestionEnrollView, QuestionModifyView, QuestionDetailView
urlpatterns = [
    path('/question', QuestionView.as_view()),
    path('/questiondetail', QuestionDetailView.as_view()),
    path('/questioninfo', QuestionInfoView.as_view()),
    path('/questionenroll', QuestionEnrollView.as_view()),
    path('/question/<int:question_id>', QuestionModifyView.as_view()),
]
