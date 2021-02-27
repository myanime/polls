from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from polls.views import PollsAdminViewSet, PollChoicesAdminViewSet, PollsViewSet, VoteAPI

router = DefaultRouter()
router.register(r'poll', PollsViewSet, basename='poll')
router.register(r'poll-admin', PollsAdminViewSet, basename='poll-admin')
router.register(r'poll-choices', PollChoicesAdminViewSet, basename='poll-choices')
urlpatterns = router.urls
urlpatterns += [
    url(r'poll/(?P<poll_id>\d+)/vote/', VoteAPI.as_view(), name="vote-api")
]
