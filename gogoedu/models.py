from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from PIL import Image
from django.utils import timezone
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django_gamification.models import PointChange, Unlockable, \
    GamificationInterface, BadgeDefinition, Badge, UnlockableDefinition,Progression,Category
from django.db.models import F

class Catagory(models.Model):
    name = models.CharField(max_length=255)
    # image = models.ImageField(upload_to='images/lesson_pics', blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('lesson', args=[str(self.id)])


class Lesson(models.Model):
    catagory = models.ForeignKey('Catagory',on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null= True)

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('lesson-detail', args=[str(self.id)])


class Word(models.Model):
    catagory = models.ForeignKey('Catagory',on_delete=models.SET_NULL, null=True)
    word = models.CharField(max_length=255)
    mean = models.CharField(max_length=255,null=True, blank=True)

    CHOICES = (
        ('V', 'Verb'),
        ('N', 'Noun'),
        ('Adj','Adjective'),
    )
    type = models.CharField(max_length=10,choices=CHOICES)
    lesson = models.ManyToManyField(Lesson)

    def __str__(self):
        """String for representing the Model object."""
        return self.word


class Test(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.SET_NULL, null=True)
    question_num = models.IntegerField()
    name = models.CharField(max_length=50, null= True)
    time = models.IntegerField(default=600)

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('test-detail', args=[str(self.id)])

    def get_test_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('test-detail', args=[str(self.id)])


class Question(models.Model):
    test = models.ForeignKey('Test', on_delete=models.SET_NULL, null=True)
    question_text = models.CharField(max_length=255)
    
    def __str__(self):
        """String for representing the Model object."""
        return self.question_text


class Choice(models.Model):
    choice_text = models.CharField(max_length=255)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        """String for representing the Model object."""
        return self.choice_text


class myUser(AbstractUser):
    avatar = models.ImageField(default='/images/profile_pics/default.jpg', upload_to='images/profile_pics')
    email = models.EmailField(_('email address'))
    interface = models.ForeignKey(GamificationInterface, on_delete=models.CASCADE,null=True)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE,null=True)
    # Resize the image
    # def save(self):
    #     super().save()
    #
    #     image = Image.open(self.avatar.path)
    #     # To resize the profile image
    #     if image.height > 400 or image.width > 400:
    #         output_size = (400, 400)
    #         image.thumbnail(output_size)
    #         image.save(self.avatar.path)


class TestResult(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    correct_answer_num = models.IntegerField(default=0)

    def __str__(self):
        """String for representing the Model object."""
        return self.test.name


class UserTest(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    is_paused = models.BooleanField(default=False)
    remain_time = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = (("user", "test"),)

    def __str__(self):
        """String for representing the Model object."""
        return self.test.name


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)


class UserWord(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    memoried = models.BooleanField(null=False,default=False)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user} - {self.word}'

    class Meta:
        unique_together = (("user", "word"),)
@receiver(post_save, sender=PointChange)
def check_unlockables(sender, instance=None, **kwargs):
    """
    Checks if the interface being used has unlocked any new Unlockables

    :param sender:
    :param kwargs:
    :return:
    """
    if instance is None:
        return

    # Find all unlockables for the interface that have less points
    # then the current interface, and update them to be unlocked
    Unlockable.objects.filter(
        interface=instance.interface,
        points_required__lte=instance.interface.points
    ).update(
        acquired=True
    )
    

# @receiver(post_save, sender=Progression)
# def check_unlock_badge(sender, instance=None, **kwargs):
#     """
#     Checks if the interface being used has unlocked any new Unlockables

#     :param sender:
#     :param kwargs:
#     :return:
#     """
#     if instance is None:
#         return

#     Badge.objects.filter(
#         progression=instance,
#         progression__target__lte=instance.progress
#     ).update(
#         acquired=True,
#         revoked=False,
#     )

@receiver(post_save, sender=GamificationInterface)
def create_badges_and_unlockables_from_new_interface(
        sender, instance, created, **kwargs):
    """
    Creates new badges from all definitions for the new interface.

    :param sender:
    :param created:
    :param kwargs:
    :return:
    """

    if not created:
        return

    for definition in BadgeDefinition.objects.all():
        Badge.objects.create_badge(definition, instance)
    category_tested=Category.objects.filter(
        name__icontains='Tested Badges', 
        description__icontains='These are the tested badges'
    ).first()
    badge_definition=BadgeDefinition.objects.filter(
            name='Bronze',
            description='Congratulation Bronze',
            points=50,
            progression_target=100,
            category=category_tested,
        ).first()
    badge=Badge.objects.filter(
        interface=instance,
        category=category_tested,
        badge_definition=badge_definition
    ).first()
    print(badge)
    badge.progression.progress=1
    badge.progression.save()
    for definition in UnlockableDefinition.objects.all():
        Unlockable.objects.create_unlockable(definition, instance)

@receiver(post_save, sender=TestResult)
def add_point_test_result(sender, instance, created, **kwargs):
    if not created:
        return
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=instance.correct_answer_num,interface=user.interface)

@receiver(post_save, sender=TestResult)
def add_progress_test_result(sender, instance, created, **kwargs):
    if not created:
        return
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    category_tested=Category.objects.filter(
        name__icontains='Tested Badges', 
        description__icontains='These are the tested badges'
    ).first()
    badge=Badge.objects.filter(
        interface=user.interface,
        category=category_tested,
        progression__progress__gte=1,
        progression__progress__lt=F('progression__target'),
    ).first()

    if badge:
        badge.increment()
        badge.progression.save()
        if badge.progression.finished and badge.next_badge:
            badge.next_badge.progression.progress=badge.progression.target+1
            badge.next_badge.progression.save()
        badge.save()

@receiver(post_save, sender=UserWord)
def add_point_learned_word(sender, instance, created, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=1,interface=user.interface)

@receiver(post_delete, sender=UserWord)
def delete_point_learned_word(sender, instance, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=-1,interface=user.interface)
