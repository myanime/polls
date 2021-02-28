from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from polls.views import PollsAdminViewSet, PollChoicesAdminViewSet, PollsViewSet, VoteAPI

router = DefaultRouter()
router.register(r'poll', PollsViewSet, basename='poll')
router.register(r'poll-admin', PollsAdminViewSet, basename='poll-admin')
router.register(r'poll-choices', PollChoicesAdminViewSet, basename='poll-choices')
urlpatterns = router.urls
urlpatterns += [
    url(r'poll/(?P<poll_id>\d+)/vote/', VoteAPI.as_view(), name="vote-api")
]

urlpatterns += [
    path('swagger-ui/', TemplateView.as_view(
        template_name='templates/swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    path('openapi', get_schema_view(), name='openapi-schema'),
]
