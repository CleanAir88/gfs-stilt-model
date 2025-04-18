from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, ReceptorViewSet, ModelGFSStiltViewSet, PollutantSourceViewSet

router = DefaultRouter()
router.register(r"model_gfs_stilt", ModelGFSStiltViewSet)
router.register(r"region", RegionViewSet)
router.register(r"receptor", ReceptorViewSet)
router.register(r"pollutant_source", PollutantSourceViewSet)

urlpatterns = router.urls