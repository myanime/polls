from uuid import uuid4

from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.utils.timezone import now
from rest_framework import viewsets, authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from polls.models import Poll, PollChoice, Respondent, Answer
from polls.serializers import PollsSerializer, PollChoicesSerializer, VoteSerializer


class VoteAPI(APIView):
    """
    This APIView allows users to vote on open polls.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, poll_id=None):
        poll = Poll.objects.get(id=poll_id)
        serializer = PollsSerializer(poll)
        return Response(serializer.data)

    @staticmethod
    def get_or_create_respondent(uuid, poll):
        respondent, created = Respondent.objects.get_or_create(uuid=uuid)
        poll.respondents.add(respondent)
        return respondent

    def post(self, request, poll_id=None):
        poll = Poll.objects.get(id=poll_id)

        serializer = VoteSerializer(data=request.data, poll=poll)
        if serializer.is_valid(raise_exception=True):
            uuid = serializer.validated_data.get('uuid')
            choices = serializer.validated_data.get('choices')
            answer = serializer.validated_data.get('answer')
            respondent = self.get_or_create_respondent(uuid, poll)

            if choices:
                respondent.choices.clear()
                for choice in choices:
                    respondents_choice = PollChoice.objects.get(choice=choice)
                    respondent.choices.add(respondents_choice)

            if answer:
                Answer.objects.get_or_create(
                    text=answer,
                    respondent=respondent,
                    poll=poll)

            return Response(PollsSerializer(poll).data)


class PollsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve Polls.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Poll.objects.prefetch_related(
        Prefetch(
            lookup='respondents',
            queryset=Respondent.objects.prefetch_related('choices', 'answer_set').all(),
        )).filter(end_date__gt=now())

    serializer_class = PollsSerializer


class PollsAdminViewSet(viewsets.ModelViewSet):
    """
    List and retrieve Polls for admin Users.
    """
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Poll.objects.prefetch_related(
        Prefetch(
            lookup='respondents',
            queryset=Respondent.objects.prefetch_related('choices', 'answer_set').all(),
        )).all()

    serializer_class = PollsSerializer


class PollChoicesAdminViewSet(viewsets.ModelViewSet):
    """
    List and retrieve Poll Choices.
    """
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [IsAdminUser]
    queryset = PollChoice.objects.all()
    serializer_class = PollChoicesSerializer


def create_admin_user():
    """
    Creates an admin user and returns the auth header
    """
    user = User.objects.create(username=str(uuid4()), is_staff=True)
    token = Token.objects.create(user=user)
    return f"-H 'Authorization: Token {token.key}'"
