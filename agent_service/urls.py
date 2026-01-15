from django.urls import path
from .views import AgentAnalyzeAPIView, recommendation_form

urlpatterns = [
    # API REST
    path('analyze/', AgentAnalyzeAPIView.as_view(), name='agent-analyze'),

    # Interface utilisateur
    path('', recommendation_form, name='recommendation-form'),
]
