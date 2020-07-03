from django.urls import include, path
from rest_framework import routers

from .views import GitHookAPIView, ToolViewSet

router = routers.SimpleRouter()
router.register(r'specs', ToolViewSet)

app_name = "tools"
urlpatterns = [
    path('', include(router.urls)),
    path('payload', GitHookAPIView.as_view())
]
