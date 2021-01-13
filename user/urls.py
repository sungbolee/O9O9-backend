from django.urls import path
from .views import SignUpView,SignInView, KakaoSignInView

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/signin/kakao', KakaoSignInView.as_view()),
]
