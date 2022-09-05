from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from ml_api.predictor.views import RegisterModelApiView

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("ml/model/register", RegisterModelApiView)


app_name = "api"
urlpatterns = router.urls
