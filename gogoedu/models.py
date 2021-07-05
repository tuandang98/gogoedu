from os import name
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.fields import BooleanField
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from PIL import Image
from django.utils import timezone
import datetime
from notifications.signals import notify
from django.db.models.signals import post_save,post_delete,pre_save
from django.dispatch import receiver
from django_gamification.models import PointChange, Unlockable, \
    GamificationInterface, BadgeDefinition, Badge, UnlockableDefinition,Progression,Category
from django.db.models import F
from ckeditor.fields import RichTextField
import random
from ckeditor_uploader.fields import RichTextUploadingField
def random_id(length):
    CHARACTERS = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(CHARACTERS) for _ in range(length))

def _default_urlid():
    return random_id(Test._meta.get_field('urlid').max_length)

class Catagory(models.Model):
    name = models.CharField(max_length=255)
    CHOICES = (
        ('N1', 'N1'),
        ('N2', 'N2'),
        ('N3','N3'),
        ('N4','N4'),
        ('N5','N5'),
    )
    level = models.CharField(max_length=10,choices=CHOICES,null=True,blank=True)
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
    kanji = models.CharField(max_length=255,null=True,blank=True)
    mean = models.CharField(max_length=255,null=True, blank=True)

    CHOICES = (
        ('V', 'Verb'),
        ('N', 'Noun'),
        ('Adj','Adjective'),
    )
    type = models.CharField(max_length=10,choices=CHOICES,null=True,blank=True)
    lesson = models.ManyToManyField(Lesson)

    def __str__(self):
        """String for representing the Model object."""
        return self.word

class Game(models.Model):
    urlid = models.CharField(max_length=10, unique=True, default=_default_urlid)
    test =  models.ForeignKey('Test', on_delete=models.SET_NULL, null=True, blank= True)
    def get_urlid(self):
        return reverse('test-detail', args=[self.urlid])

class Test(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.SET_NULL, null=True, blank= True)
    kanji_lesson = models.ForeignKey('KanjiLesson', on_delete=models.SET_NULL, null=True, blank= True)
    grammar_lesson = models.ForeignKey('GrammarLesson', on_delete=models.SET_NULL, null=True, blank= True)
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
    test = models.ForeignKey('Test', on_delete=models.CASCADE,null=True,blank=True)
    reading = models.ForeignKey('Reading', on_delete=models.CASCADE,null=True,blank=True)
    listening = models.ForeignKey('Listening', on_delete=models.CASCADE,null=True,blank=True)
    correct_answer_num = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, blank=True)



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





class UserWord(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    memoried = models.BooleanField(null=False,default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user} - {self.word}'

    class Meta:
        unique_together = (("user", "word"),)

class GrammarLevel(models.Model):
    name = models.CharField(max_length=255)
    CHOICES = (
        ('N1', 'N1'),
        ('N2', 'N2'),
        ('N3','N3'),
        ('N4','N4'),
        ('N5','N5'),
    )
    level = models.CharField(max_length=2,choices=CHOICES,null=True,blank=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('grammar-lesson', args=[str(self.id)])

class GrammarLesson(models.Model):
    name = models.CharField(max_length=255)
    grammar_level = models.ForeignKey(GrammarLevel, on_delete=models.CASCADE)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('grammar-detail', kwargs={'pk':self.id,'grammar_lesson_id': self.grammar_level.id})

class Grammar(models.Model):
    name = models.CharField(max_length=255)
    connect = models.CharField(max_length=255,default="ALL")
    grammar_lesson = models.ForeignKey(GrammarLesson, on_delete=models.CASCADE)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

class GrammarMean(models.Model):
    mean = models.CharField(max_length=255)
    grammar = models.ForeignKey(Grammar, on_delete=models.CASCADE)

class Example(models.Model):
    example = models.CharField(max_length=255)
    grammar_mean = models.ForeignKey(GrammarMean, on_delete=models.CASCADE)

class KanjiLevel(models.Model):
    name = models.CharField(max_length=255)
    CHOICES = (
        ('N1', 'N1'),
        ('N2', 'N2'),
        ('N3','N3'),
        ('N4','N4'),
        ('N5','N5'),
    )
    level = models.CharField(max_length=2,choices=CHOICES,null=True,blank=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('kanji-lesson', args=[str(self.id)])

class KanjiLesson(models.Model):
    name = models.CharField(max_length=255)
    kanji_level = models.ForeignKey(KanjiLevel, on_delete=models.CASCADE)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('kanji-detail', kwargs={'pk':self.id,'kanji_lesson_id': self.kanji_level.id})

class Kanji(models.Model):
    kanji = models.CharField(max_length=255)
    reading = models.CharField(max_length=255)
    definition = models.CharField(max_length=255)
    kanji_lesson = models.ForeignKey(KanjiLesson, on_delete=models.CASCADE)
    def __str__(self):
        """String for representing the Model object."""
        return self.kanji
    


class ExampleKanji(models.Model):
    example = models.CharField(max_length=255)
    reading = models.CharField(max_length=255)
    definition = models.CharField(max_length=255)
    kanji = models.ForeignKey(Kanji, on_delete=models.CASCADE)
    

class ReadingLevel(models.Model):
    name = models.CharField(max_length=255)
    CHOICES = (
        ('N1', 'N1'),
        ('N2', 'N2'),
        ('N3','N3'),
        ('N4','N4'),
        ('N5','N5'),
    )
    level = models.CharField(max_length=2,choices=CHOICES,null=True,blank=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('reading-lesson', args=[str(self.id)])

class ReadingLesson(models.Model):
    name = models.CharField(max_length=255)
    reading_level = models.ForeignKey(ReadingLevel, on_delete=models.CASCADE)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('reading-detail', kwargs={'pk':self.id,'reading_lesson_id': self.reading_level.id})

class Reading(models.Model):
    text = RichTextUploadingField(null=True)
    mondai = models.CharField(max_length=255)
    reading_lesson = models.ForeignKey(ReadingLesson, on_delete=models.CASCADE)

class ListeningLevel(models.Model):
    name = models.CharField(max_length=255)
    CHOICES = (
        ('N1', 'N1'),
        ('N2', 'N2'),
        ('N3','N3'),
        ('N4','N4'),
        ('N5','N5'),
    )
    level = models.CharField(max_length=2,choices=CHOICES,null=True,blank=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('listening-lesson', args=[str(self.id)])

class ListeningLesson(models.Model):
    name = models.CharField(max_length=255)
    listening_level = models.ForeignKey(ListeningLevel, on_delete=models.CASCADE)
    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('listening-detail', kwargs={'pk':self.id,'listening_lesson_id': self.listening_level.id})

class Listening(models.Model):
    text = RichTextUploadingField(null=True)
    file = models.FileField(upload_to='musics/')
    listening_lesson = models.ForeignKey(ListeningLesson, on_delete=models.CASCADE)

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
    unlocks = Unlockable.objects.filter(
        interface=instance.interface,
        points_required__lte=instance.interface.points,
        acquired=False,
    )
    user = myUser.objects.filter(interface=instance.interface).first()
    for unlock in unlocks:
        unlock.acquired= True
        if unlock.name == 'Mission 20 quests':
            missionw = Mission.objects.filter(type="W",user=user).update(name="Learn 20 vocabulary",description='Learn 20 vocabulary',target=20,point=75)
            missionk = Mission.objects.filter(type="K",user=user).update(name="Learn 20 kanji",description='Learn 20 kanji',target=20,point=75)
            missionr = Mission.objects.filter(type="R",user=user).update(name="Learn 20 reading",description='Learn 20 reading',target=20,point=75)
            missionl = Mission.objects.filter(type="L",user=user).update(name="Learn 20 listening",description='Learn 20 listening',target=20,point=75)
            missiong = Mission.objects.filter(type="G",user=user).update(name="Learn 20 grammar",description='Learn 20 grammar',target=20,point=75)
        unlock.save()

    
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
class Question(models.Model):
    test = models.ForeignKey('Test', on_delete=models.SET_NULL, null=True,blank=True)
    reading = models.ForeignKey(Reading, on_delete=models.SET_NULL, null=True,blank=True)
    listening = models.ForeignKey(Listening, on_delete=models.SET_NULL, null=True,blank=True)
    question = RichTextUploadingField(null=True)
    


class Choice(models.Model):
    choice_text = models.CharField(max_length=255)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        """String for representing the Model object."""
        return self.choice_text
class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
class UserKanji(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    kanji = models.ForeignKey(Kanji, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user} - {self.kanji}'

    class Meta:
        unique_together = (("user", "kanji"),)
class UserGrammar(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    grammar = models.ForeignKey(Grammar, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user} - {self.grammar}'

    class Meta:
        unique_together = (("user", "grammar"),)
class todo(models.Model):
    name = models.TextField(max_length=255)
    user = models.ForeignKey(myUser, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
@receiver(post_save, sender=GamificationInterface)
def create_badges_and_unlockables_from_new_interface(
        sender, instance, created, **kwargs):

    if not created:    
        return

    for definition in BadgeDefinition.objects.all():
        Badge.objects.create_badge(definition, instance)
    category_tested=Category.objects.filter(
        name='Tested Badges', 
        description='These are the tested badges'
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
    category_learned=Category.objects.filter(
            name='Learned', 
            description='These are the learned badges'
        ).first()
    category_kanji=Category.objects.filter(name='Kanji', description='These are the kanji badges').first()
        
    badge_definition2=BadgeDefinition.objects.filter(
            name='100 Words learned',
            description='Learned 100 words',
            points=50,
            progression_target=100,
            category=category_learned,
                ).first()
    badge2=Badge.objects.filter(
            interface=instance,
            category=category_learned,
            badge_definition=badge_definition2
        ).first()
    badge_definition3=BadgeDefinition.objects.filter(
            name='100 Kanjis learned',
            description='Learned 100 kanji',
            points=50,
            progression_target=100,
            category=category_kanji,
                ).first()
    badge3=Badge.objects.filter(
            interface=instance,
            category=category_kanji,
            badge_definition=badge_definition3
        ).first()
    
    badge2.progression.progress=1
    badge2.progression.save()
    badge3.progression.progress=1
    badge3.progression.save()
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
    if instance.reading is not None:
        mission=Mission.objects.filter(user=instance.user,type="R").first()
        if mission.complete is False:
            mission.process+=1
            mission.save()
    if instance.listening is not None:
        mission=Mission.objects.filter(user=instance.user,type="L").first()
        if mission.complete is False:
            mission.process+=1
            mission.save()

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
        if badge.progression.finished:
            message='Congratulations you get '+str(badge.points)+' points title of '+ str(badge.name)
            PointChange.objects.create(amount=badge.points,interface=user.interface)
            notify.send(user, recipient=user, verb='Notification',description=message)
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

    mission_word=Mission.objects.filter(user=instance.user,type="W").first()
    if mission_word.complete is False:
        mission_word.process+=1
        mission_word.save()
    category_learned=Category.objects.filter(
            name='Learned', 
            description='These are the learned badges'
        ).first()
    badge=Badge.objects.filter(
        interface=user.interface,
        category=category_learned,
        progression__progress__gte=1,
        progression__progress__lt=F('progression__target'),
    ).first()

    if badge:
        badge.increment()
        badge.progression.save()
        if badge.progression.finished:
            message='Congratulations you get '+str(badge.points)+' points title of '+ str(badge.name)
            PointChange.objects.create(amount=badge.points,interface=user.interface)
            notify.send(user, recipient=user, verb='Notification',description=message)
        if badge.progression.finished and badge.next_badge:
            badge.next_badge.progression.progress=badge.progression.target+1
            badge.next_badge.progression.save()
        badge.save()

@receiver(post_delete, sender=UserWord)
def delete_point_learned_word(sender, instance, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=-1,interface=user.interface)
    
@receiver(post_save, sender=UserKanji)
def add_point_learned_kanji(sender, instance, created, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=1,interface=user.interface)
    mission_kanji=Mission.objects.filter(user=instance.user,type="K").first()
    if mission_kanji.complete is False:
        mission_kanji.process+=1
        mission_kanji.save()
    category_kanji=Category.objects.filter(
            name='Kanji', 
            description='These are the kanji badges'
        ).first()
    badge=Badge.objects.filter(
        interface=user.interface,
        category=category_kanji,
        progression__progress__gte=1,
        progression__progress__lt=F('progression__target'),
    ).first()

    if badge:
        badge.increment()
        badge.progression.save()
        if badge.progression.finished:
            message='Congratulations you get '+str(badge.points)+' points title of '+ str(badge.name)
            PointChange.objects.create(amount=badge.points,interface=user.interface)
            notify.send(user, recipient=user, verb='Notification',description=message)
        if badge.progression.finished and badge.next_badge:
            badge.next_badge.progression.progress=badge.progression.target+1
            badge.next_badge.progression.save()
        badge.save()
    
@receiver(post_delete, sender=UserKanji)
def delete_point_learned_kanji(sender, instance, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=-1,interface=user.interface)
    
@receiver(post_save, sender=UserGrammar)
def add_point_learned_grammar(sender, instance, created, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=1,interface=user.interface)
   

@receiver(post_delete, sender=UserGrammar)
def delete_point_learned_grammar(sender, instance, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    PointChange.objects.create(amount=-1,interface=user.interface)
    mission_grammar=Mission.objects.filter(user=instance.user,type="G").first()
    if mission_grammar.complete is False:
        mission_grammar.process+=1
        mission_grammar.save()
class Mission(models.Model):
    user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    point = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(null= True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    process = models.IntegerField(null= True,blank=True)
    target = models.IntegerField(null= True,blank=True)
    CHOICES = (
        ('W', 'Word'),
        ('G', 'Grammar'),
        ('R','Reading'),
        ('L','Listening'),
        ('K','Kanji'),
    )
    complete = BooleanField(default=False)
    type = models.CharField(max_length=10,choices=CHOICES,null=True,blank=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.name


    

@receiver(pre_save, sender=myUser)
def misson_daily_login(sender, instance, **kwargs):
    user=myUser.objects.filter(
        id=instance.id
    ).first()
    if user is not None:
        if user.interface is not None:
            if user.last_login is None:
                mission = Mission.objects.filter(user=user,name="DailyLogin").first()
                missionw= Mission.objects.create(
                        name="Learn 10 vocabulary",
                        user=user,
                        description='Learn 10 vocabulary',
                        process=0,
                        target=10,
                        point=50,
                        type="W",
                        )
                missionk= Mission.objects.create(
                        name="Learn 10 kanji",
                        user=user,
                        description='Learn 10 kanji',
                        process=0,
                        target=10,
                        point=50,
                        type="K",
                        )   
                missionr= Mission.objects.create(
                        name="Learn 10 Reading",
                        user=user,
                        description='Learn 10 Reading',
                        process=0,
                        target=10,
                        point=50,
                        type="R",
                        )   
                missionl= Mission.objects.create(
                        name="Learn 10 Listening",
                        user=user,
                        description='Learn 10 Listening',
                        process=0,
                        target=10,
                        point=50,
                        type="L",
                        )
                missiong= Mission.objects.create(
                        name="Learn 10 Grammar",
                        user=user,
                        description='Learn 10 Grammar',
                        process=0,
                        target=10,
                        point=50,
                        type="G",
                        )      
                PointChange.objects.create(amount=mission.point,interface=user.interface)
                message='You get '+str(mission.point)+' points from the login quest'
                notify.send(user, recipient=user, verb='Notification',description=message)
                
            else:
                
                mission = Mission.objects.filter(user=user,name="DailyLogin").first()
                if(instance.last_login.date()-user.last_login.date()>=datetime.timedelta(1)):
                    
                    if(datetime.date.today()-mission.updated_at.date()==datetime.timedelta(1)):
                        if(mission.process<5):
                            mission.point=mission.point+50
                            mission.process=mission.process+1
                            mission.save()
                    if(datetime.date.today()-mission.updated_at.date()>=datetime.timedelta(2)):
                        
                        mission.point=50
                        mission.process=1
                        mission.save()
                    message='You get '+str(mission.point)+' points from the login quest'
                    notify.send(user, recipient=user, verb='Notification',description=message)
                    PointChange.objects.create(amount=mission.point,interface=user.interface)
@receiver(post_save, sender=Mission)
def complete_misson(sender, instance, created, **kwargs):
    user=myUser.objects.filter(
        id=instance.user.id
    ).first()
    if instance.process>=instance.target and instance.complete is False:
        misson = Mission.objects.filter(id=instance.id).first()
        misson.complete=True
        PointChange.objects.create(amount=instance.point,interface=user.interface)
        message='You get '+str(misson.point)+'points from the daily quest'
        notify.send(user, recipient=user, verb='Notification',description=message)
        misson.save()

