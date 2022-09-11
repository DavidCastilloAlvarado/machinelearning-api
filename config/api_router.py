from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from ml_api.predictor.views import (
    PerformPredictionApiView,
    PredictionsHistoryApiView,
    RegisterModelApiView,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("ml/model/register", RegisterModelApiView)
router.register("ml/model/prediction/history", PredictionsHistoryApiView)
router.register(
    "ml/model/heart-failure/prediction", PerformPredictionApiView, basename="prediction"
)


app_name = "api"
urlpatterns = router.urls
