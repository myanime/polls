from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls.models import Poll, PollChoice


class PollChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollChoice
        fields = ('choice',)


class VoteSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=False)
    choices = serializers.ListField(required=False)
    answer = serializers.CharField(required=False)

    def __init__(self, **kwargs):
        self.poll = kwargs.pop('poll')
        super(VoteSerializer, self).__init__(**kwargs)

    def validate_poll_date(self):
        if self.poll.end_date < now():
            raise ValidationError("The poll has expired")

    @staticmethod
    def validate_correct_answer_type(multiple_choice_question, answer, choices):
        if multiple_choice_question and answer:
            raise ValidationError("This is a multiple choice poll")
        if not multiple_choice_question and choices:
            raise ValidationError("This is a long form answer poll")

    @staticmethod
    def validate_only_one_type_of_answer(answer, choices):
        if answer and choices:
            raise ValidationError("Select either a choice or write an answer, not both.")

    @staticmethod
    def validate_at_least_one_type_of_answer(answer, choices):
        if not answer and not choices:
            raise ValidationError("You must either select or write an answer")

    @staticmethod
    def validate_multiple_choice_has_choices(multiple_choice_question, choices):
        if multiple_choice_question and not choices:
            raise ValidationError("No choices were selected.")

    def validate_all_choices(self, choices):
        poll_choices = [choice.choice for choice in self.poll.choices.all()]
        if not all([choice in poll_choices for choice in choices]):
            raise ValidationError(f'The selected choice/s are invalid choice.')

    def validate(self, data):
        answer = data.get('answer')
        choices = data.get('choices')
        multiple_choice_question = self.poll.choices.exists()

        self.validate_poll_date()
        self.validate_correct_answer_type(multiple_choice_question, answer, choices)
        self.validate_only_one_type_of_answer(answer, choices)
        self.validate_multiple_choice_has_choices(multiple_choice_question, choices)
        self.validate_at_least_one_type_of_answer(answer, choices)
        if choices:
            self.validate_all_choices(choices)
        return data


class PollsSerializer(serializers.ModelSerializer):
    choices = PollChoicesSerializer(many=True, required=False)
    start_date = serializers.DateTimeField(required=False)
    respondents = serializers.SerializerMethodField()

    def get_respondents(self, obj):
        poll = obj
        respondent_info = []
        for respondent in poll.respondents.all():
            respondent_uuid = respondent.uuid
            multiple_choice = list(respondent.choices.all().values_list('choice', flat=True))
            respondent_answers = respondent.answer_set.filter(poll=poll)

            if multiple_choice or respondent_answers:
                info = {
                    'uuid': respondent_uuid
                }
                if multiple_choice:
                    info['choices'] = multiple_choice
                if respondent_answers:
                    count = 0
                    for respondent_answer in respondent_answers:
                        info[f'answer-{count}'] = respondent_answer.text
                        count += 1
                respondent_info.append(info)
        return respondent_info

    def update(self, instance, validated_data):
        if instance.start_date:
            validated_data.pop('start_date')
        choices = self.get_choices(validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.choices.clear()
        self.add_choices_for_poll(choices, instance)
        return instance

    def create(self, validated_data):
        if not validated_data.get('start_date'):
            raise ValidationError('Please enter a start date')
        choices = self.get_choices(validated_data)
        poll = Poll.objects.create(**validated_data)
        self.add_choices_for_poll(choices, poll)
        return poll

    @staticmethod
    def add_choices_for_poll(choices, poll):
        if choices:
            for choice in choices:
                new_choice, created = PollChoice.objects.get_or_create(choice=choice.get('choice'))
                poll.choices.add(new_choice)

    @staticmethod
    def get_choices(validated_data):
        choices = validated_data.get('choices')
        if choices:
            validated_data.pop('choices')
        return choices

    class Meta:
        model = Poll
        fields = ('id', 'title', 'end_date', 'question', 'choices', 'start_date', 'respondents')
