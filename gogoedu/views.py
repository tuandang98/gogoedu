
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail.backends import console
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from background_task.models import Task
from .forms import RegisterForm
from django.views import generic
from django.conf import settings
from django.template import loader
from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django_email_verification import sendConfirm
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.forms.models import model_to_dict
from json import dumps
from .forms import RegisterForm, UserUpdateForm
from gogoedu.models import Grammar, GrammarLevel, myUser, Lesson, Word, Catagory, Test, UserTest, Question, Choice, UserAnswer, UserWord, \
    TestResult,GrammarLevel,GrammarLesson,GrammarMean,Example,KanjiLesson,KanjiLevel,Kanji,Reading,ReadingLesson,ReadingLevel,ListeningLevel,ListeningLesson,Listening

from PIL import Image

from django.shortcuts import get_object_or_404
from django.db import transaction

from django.core.exceptions import PermissionDenied
from background_task import background

from django.db.models import Avg, Count, Min, Sum, Q
import random 
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView, RedirectView
from django_gamification.models import Badge,BadgeDefinition, Category, UnlockableDefinition, GamificationInterface

import datetime

def index(request):
    return render(request, 'index.html')


def change_language(request):
    response = HttpResponseRedirect('/')
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            if language != settings.LANGUAGE_CODE and [lang for lang in settings.LANGUAGES if lang[0] == language]:
                redirect_path = f'/{language}/'
            elif language == settings.LANGUAGE_CODE:
                redirect_path = '/'
            else:
                return response
            from django.utils import translation
            translation.activate(language)
            response = HttpResponseRedirect(redirect_path)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response


class Profile(LoginRequiredMixin, generic.DetailView):
    model = myUser

    def get_context_data(self, **kwargs):
        object_list = myUser.objects.filter()
        context = super(Profile, self).get_context_data(object_list=object_list, **kwargs)
        user = self.request.user
        if not user.avatar:
            avatar = '/media/images/profile_pics/default.jpg'
        else:
            avatar = user.avatar.url
        context['avatar'] = avatar
        return context


def register(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'GoGoEdu - Activate your account.'
                message = render_to_string('registration/verify_mail_template.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                plain_message = strip_tags(message)
                to_email = form.cleaned_data.get('email')
                send_mail(mail_subject, plain_message, settings.EMAIL_HOST_USER, [to_email], html_message=message)
                return redirect('account-activation', user.id)
                # return HttpResponseRedirect(reverse('index'))
        else:
            form = RegisterForm()

        return render(request, "registration/register.html", {"form": form})
    else:
        return redirect('index')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = myUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, myUser.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.interface=GamificationInterface.objects.create()
        user.save()
        return render(request, "registration/activation_success.html", {'user_is_active': True})
    else:
        return render(request, "registration/activation_success.html", {'user_is_active': False})


def activation_request(request, pk):
    user = get_object_or_404(myUser, pk=pk)
    if user.is_active:
        return redirect('index')
    else:
        return render(request, "registration/account_activate.html", {'username': user.username})


class Lesson_detail(LoginRequiredMixin, generic.DetailView, MultipleObjectMixin):
    model = Lesson
    paginate_by = 20

    def get_success_url(self):
        return reverse('lesson-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        lesson = self.get_object()
        object_list = Word.objects.filter(lesson=lesson)
        context = super(Lesson_detail, self).get_context_data(object_list=object_list, **kwargs)
        tests = lesson.test_set.all()
        user_test_list = []
        marked_word_list = []
        new_list = []
        tested_list = []
        for test in tests:
            if UserTest.objects.filter(user=self.request.user.id, test=test.id).first():
                user_test_list.append(UserTest.objects.filter(user=self.request.user.id, test=test.id).first())
                tested_list.append(test)

        for word in object_list:
            if not UserWord.objects.filter(user=self.request.user.id, word=word.id).first():
                new_list.append(word)
            else:
                marked_word_list.append(word)
        context['user_test_list'] = user_test_list
        context['tested_list'] = tested_list
        context['marked_word_list'] = marked_word_list
        context['new_list'] = new_list
        # if UserTest.objects.filter(user=self.request.user, test=lesson.test_set.first.id):
        #     context['my_test'] = UserTest.objects.filter(user=self.request.user, test=lesson.test).first()
        return context


class CatagoryListView(generic.ListView):
    model = Catagory
    paginate_by = 3

    def get_queryset(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.model.objects.filter(name__icontains=name)
        else:
            object_list = self.model.objects.filter()
        return object_list


class CatagoryDetailView(generic.DetailView, MultipleObjectMixin):
    model = Catagory
    paginate_by = 10

    def get_context_data(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.lesson_set.filter(name__icontains=name)
        else:
            object_list = self.object.lesson_set.all()
        context = super(CatagoryDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context


@login_required
def profile_update(request, pk):
    user = get_object_or_404(myUser, pk=pk)
    if not user.avatar:
        avatar = '/media/images/profile_pics/default.jpg'
    else:
        avatar = user.avatar.url
    if request.user == user:
        if request.method == "POST":
            form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, f'Your account was updated!')
                return redirect('profile-update', pk)
        else:
            form = UserUpdateForm(instance=user)

        return render(request, 'gogoedu/myuser_update.html', {'form': form, 'avatar': avatar})
    else:
        return redirect('index')


def is_authenticated(request):
    if not request.user.is_authenticated:
        raise PermissionDenied


def test_detail_view(request, pk):
    is_authenticated(request)
    test = get_object_or_404(Test, pk=pk)

    if UserTest.objects.filter(user=request.user, test=test):
        my_test = UserTest.objects.filter(user=request.user, test=test).first()
        test_time = my_test.remain_time
        my_test.is_paused = False
        my_test.save()
    else:
        my_test = UserTest(user=request.user, test=test)
        test_time = test.time
        my_test.save()

    choices = UserAnswer.objects.filter(
        user=request.user,
        question__test=test,
    )
    listchoices = []
    for choices1 in choices:
        listchoices.append(choices1.choice)

    if request.method == 'POST':
        data = {}
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            question_id = key.split('-')[1]
            choice_id = request.POST.get(key)
            data[question_id] = choice_id
        perform_test(request.user, data, test)
        if UserTest.objects.filter(user=request.user, test=test):
            UserTest.objects.filter(user=request.user, test=test).delete()
        Task.objects.filter(task_params='[['+str(request.user.id)+', '+str(test.id)+'], {}]').delete()
        return redirect(reverse('show_results', args=(test.id,)))
    if not Task.objects.filter(task_params='[['+str(request.user.id)+', '+str(test.id)+'], {}]'):
        countdown_time(request.user.id,test.id, schedule=timedelta(seconds=test_time))
    task=Task.objects.filter(task_params='[['+str(request.user.id)+', '+str(test.id)+'], {}]')
    if not timezone.now()>task[0].run_at:
        time=task[0].run_at-timezone.now()
        set_time=time.seconds
    else:
        set_time=0
    
    
    context = {
        'test': test,
        'test_time': set_time,
        'my_test': my_test,
        'choices': listchoices,
    }
    return render(request, 'gogoedu/test_detail.html', context)


class TestSave(generic.View):

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        test = get_object_or_404(Test, pk=pk)
        data = {}
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            question_id = key.split('-')[1]
            choice_id = request.POST.get(key)
            data[question_id] = choice_id
        perform_test(request.user, data, test)
        return JsonResponse({'data': data}, status=200)


class TestPause(generic.View):

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        test = get_object_or_404(Test, pk=pk)
        my_test = UserTest.objects.get(user=request.user, test=test)
        my_test.is_paused = True
        my_test.remain_time = request.POST.get('test_time')
        my_test.save()
        Task.objects.filter(task_params='[['+str(request.user.id)+', '+str(test.id)+'], {}]').delete()
        # my_test.update(is_paused=not my_test.is_paused)
        
        return redirect('lesson-detail', test.lesson.id)


class SuspiciousOperation(Exception):
    def __init__(self, value):
        print(value)


def perform_test(user, data, test):
    with transaction.atomic():
        UserAnswer.objects.filter(user=user, question__test=test).delete()
        for question_id, choice_id in data.items():
            question = Question.objects.get(id=question_id)
            choice_id = int(choice_id)
            if choice_id not in question.choice_set.values_list('id', flat=True):
                raise SuspiciousOperation('Choice is not valid for this question')
            UserAnswer.objects.create(user=user,
                                      question=question,
                                      choice_id=choice_id, )


def calculate_score(user, test):
    questions = Question.objects.filter(test=test)
    correct_choices = UserAnswer.objects.filter(
        user=user,
        question__test=test,
        choice__correct=True
    )
    score = TestResult(user=user, test=test, correct_answer_num=correct_choices.count())
    score.save()
    return correct_choices.count()



def show_form_correct(request, pk):
    is_authenticated(request)
    test = Test.objects.get(id=pk)
    questions = Question.objects.filter(test=test)
    choices = UserAnswer.objects.filter(
        user=request.user,
        question__test=test,
    )
    listchoices = []
    for choices1 in choices:
        listchoices.append(choices1.choice)
    context = {
        'test': test,
        'score': calculate_score(request.user, test),
        'choices': listchoices,
    }
    UserAnswer.objects.filter(user=request.user, question__test=test).delete()
    return render(request, 'gogoedu/show_results.html', context)


class MarkLearned(generic.View):

    def post(self, request, pk, wordid):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        user_word = UserWord()
        user_word.user = myUser.objects.get(id=request.user.id)
        user_word.word = Word.objects.get(id=wordid)
        if not UserWord.objects.filter(user=request.user.id, word=wordid).first():
            user_word.save()
            learned = True
        else:
            UserWord.objects.filter(user=request.user.id, word=wordid).delete()
            learned = False
        return JsonResponse({'word': model_to_dict(user_word), 'learned': learned}, status=200)


def summary_detail_view(request):
    is_authenticated(request)
    template = loader.get_template('gogoedu/summary.html')
    list_learned = UserWord.objects.filter(user=request.user.id)
    list_memoried = UserWord.objects.filter(user=request.user.id, memoried=True)
    list_tested = TestResult.objects.filter(user=request.user.id)

    page = request.GET.get('page', 1)
    paginator1 = Paginator(list_tested, 5)
    
    try:
        tested_paged = paginator1.page(page)
    except PageNotAnInteger:
        tested_paged = paginator1.page(1)
    except EmptyPage:
        tested_paged = paginator1.page(paginator1.num_pages)

    paginator2 = Paginator(list_memoried, 2)
    try:
        memoried_paged = paginator2.page(page)
    except PageNotAnInteger:
        memoried_paged = paginator2.page(1)
    except EmptyPage:
        memoried_paged = paginator2.page(paginator2.num_pages)

    paginator3 = Paginator(list_learned, 10)
    try:
        learned_paged = paginator3.page(page)
    except PageNotAnInteger:
        learned_paged = paginator3.page(1)
    except EmptyPage:
        learned_paged = paginator3.page(paginator3.num_pages)
    context = {"list_tested": tested_paged,
               'list_learned': learned_paged,
               'list_memoried': memoried_paged,
               'total_learned': list_learned,
               'total_memoried': list_memoried,
               'total_tested': list_tested,
               }
    return HttpResponse(template.render(context, request))


def flashcard_view(request):
    lesson_query_set = Lesson.objects.all().order_by('name')
    context = {'topics': lesson_query_set}  
    return render(request, 'flashcard.html', context)
def view_card_set(request, pk):
    lesson = get_object_or_404(Lesson, id = pk)
    word_list = lesson.word_set.all()
    card_object = word_list.first()	   
    page = request.GET.get('page', 1)
    paginator = Paginator(word_list, 1)
    
    try:
        word_list_paged = paginator.page(page)
    except PageNotAnInteger:
        word_list_paged = paginator.page(1)
    except EmptyPage:
        word_list_paged = paginator.page(paginator.num_pages)

    context = {'lesson': lesson, 'card_object': word_list_paged}
    return render(request, 'gogoedu/view_cards.html', context)

def leaderboard_view(request):
    template = loader.get_template('leaderboard.html')
    top_points = myUser.objects.annotate(average_correct=Avg('testresult__correct_answer_num', distinct=True),num_tests=Count('testresult', distinct=True),num_words=Count('userword', distinct=True),num_badges=Count('interface__badge',filter=Q(interface__badge__acquired=True, interface__badge__revoked=False), distinct=True)).exclude(interface=None)
    top_tested = myUser.objects.annotate(average_correct=Avg('testresult__correct_answer_num', distinct=True),num_tests=Count('testresult', distinct=True),num_words=Count('userword', distinct=True)).order_by('-num_tests')[:3]
       
    top_learned_word = myUser.objects.annotate(average_correct=Avg('testresult__correct_answer_num', distinct=True),num_tests=Count('testresult', distinct=True),num_words=Count('userword', distinct=True)).order_by('-num_tests')[:3]

    context = {"top_points": sorted(top_points,  key=lambda p: p.interface.points,reverse=True)[:3],
                "top_tested":top_tested,
                "top_learned_word":top_learned_word,
               }
    return HttpResponse(template.render(context, request))

def flashcard_test(request, pk):
    template = loader.get_template('gogoedu/flashcard_test.html')
    lesson = get_object_or_404(Lesson, id = pk)
    word_list = lesson.word_set.all()
    id_list = word_list.values_list('id', flat=True)
    
    random_profiles_id_list = random.sample(list(id_list), min(len(id_list), 6))
    query_set = word_list.filter(id__in=random_profiles_id_list)
    
    query_set2 = random.sample(list(query_set), min(len(query_set), 6))

    context = {"word_list1": query_set,
                "word_list2":query_set2,
               }
    return HttpResponse(template.render(context, request))


    
def privacy_view(request):
    return render(request, 'privacy.html')

class GetTestInfo(generic.View):

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        if UserTest.objects.filter(user=request.user.id, test=request.GET.get('test_id',)).first():
            my_test = UserTest.objects.filter(user=request.user.id, test=request.GET.get('test_id',)).first()
            tested = True
        else:
            my_test = UserTest(user=request.user, test=Test.objects.get(id=request.GET.get('test_id',)))
            tested = False
        return JsonResponse({'my_test_remain_time': my_test.remain_time, 'tested': tested}, status=200)
@background(schedule=20)
def countdown_time(user_id,test_id):
    test = get_object_or_404(Test, pk=test_id)
    user=myUser.objects.get(id=user_id)
    choices = UserAnswer.objects.filter(
        user=user,
        question__test=test,
    )
    listchoices = []
    for choices1 in choices:
        listchoices.append(choices1.choice)
    
    UserAnswer.objects.filter(user=user, question__test=test).delete()
    kq=calculate_score(user, test)
    if UserTest.objects.filter(user=user, test=test):
        UserTest.objects.filter(user=user, test=test).delete()

class BadgeView(TemplateView):
    template_name = 'badge.html'

    def get_context_data(self, **kwargs):
        context = super(BadgeView, self).get_context_data(**kwargs)

        user_data = []
        for user in myUser.objects.all():
            acquired_badges = user.interface.badge_set.filter(acquired=True, revoked=False)
            award_badge_ids = [b.id for b in user.interface.badge_set.filter(acquired=False)]
            revoke_badge_ids = [b.id for b in acquired_badges]

            user_data.append({
                'id': user.id,
                'badges': ', '.join([b.name for b in acquired_badges]),
                'points': user.interface.points,
                'random_award_badge_id': random.choice(award_badge_ids) if award_badge_ids else None,
                'random_revoke_badge_id': random.choice(revoke_badge_ids) if revoke_badge_ids else None
            })

        context['users'] = user_data

        return context


class AwardBadgeView(RedirectView):
    pattern_name = 'badge'

    def get_redirect_url(self, *args, **kwargs):
        badge_id = kwargs.pop('badge_id')

        badge = Badge.objects.filter(id=badge_id).first()
        badge.increment()
        badge.save()

        return super(AwardBadgeView, self).get_redirect_url(*args, **kwargs)


class RevokeBadgeView(RedirectView):
    pattern_name = 'badge'

    def get_redirect_url(self, *args, **kwargs):
        badge_id = kwargs.pop('badge_id')

        badge = Badge.objects.filter(id=badge_id).first()
        badge.force_revoke()
        badge.acquired = False  # We don't actually want to revoke it entirely in this example
        badge.revoked = False
        badge.save()

        return super(RevokeBadgeView, self).get_redirect_url(*args, **kwargs)

class SetBadgeView(RedirectView):
    pattern_name = 'profile-detail'

    def get_redirect_url(self, *args, **kwargs):
        badge_id = kwargs.pop('badge_id')
        user_id = kwargs.pop('pk')
        badge = Badge.objects.filter(id=badge_id).first()
        user = myUser.objects.filter(id=user_id).first()
        user.badge=badge
        user.save()

        return super(SetBadgeView, self).get_redirect_url(*args, pk=user_id)
def Alphabet(request):
    return render(request, 'gogoedu/Alphabet.html')
class GrammarLevelListView(generic.ListView):
    model = GrammarLevel
    paginate_by = 3

    def get_queryset(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.model.objects.filter(name__icontains=name)
        else:
            object_list = self.model.objects.filter()
        return object_list

class GrammarLevelDetailView(generic.DetailView, MultipleObjectMixin):
    model = GrammarLevel
    paginate_by = 10
    def get_context_data(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.grammarlesson_set.filter(name__icontains=name)
        else:
            object_list = self.object.grammarlesson_set.all()
        context = super(GrammarLevelDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context

class Grammar_lesson_detail(LoginRequiredMixin, generic.DetailView, MultipleObjectMixin):
    model = GrammarLesson
    paginate_by = 20

    def get_success_url(self):
        print("12131231313123123")
        return reverse('grammar-detail', kwargs={'pk': self.object.pk,'grammar_lesson_id':self.object.grammar_level.id})
        
        

    def get_context_data(self, **kwargs):
        lesson = self.get_object()
        print(self.object)
        object_list = Grammar.objects.filter(grammar_lesson=lesson)
        context = super(Grammar_lesson_detail, self).get_context_data(object_list=object_list, **kwargs)
        # tests = lesson.test_set.all()
        # user_test_list = []
        # marked_word_list = []
        # new_list = []
        # tested_list = []
        # for test in tests:
        #     if UserTest.objects.filter(user=self.request.user.id, test=test.id).first():
        #         user_test_list.append(UserTest.objects.filter(user=self.request.user.id, test=test.id).first())
        #         tested_list.append(test)

        # for word in object_list:
        #     if not UserWord.objects.filter(user=self.request.user.id, word=word.id).first():
        #         new_list.append(word)
        #     else:
        #         marked_word_list.append(word)
        # context['user_test_list'] = user_test_list
        # context['tested_list'] = tested_list
        # context['marked_word_list'] = marked_word_list
        # context['new_list'] = new_list
        # if UserTest.objects.filter(user=self.request.user, test=lesson.test_set.first.id):
        #     context['my_test'] = UserTest.objects.filter(user=self.request.user, test=lesson.test).first()
        return context
        
class KanjiLevelListView(generic.ListView):
    model = KanjiLevel
    paginate_by = 3

    def get_queryset(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.model.objects.filter(name__icontains=name)
        else:
            object_list = self.model.objects.filter()
        return object_list

class KanjiLevelDetailView(generic.DetailView, MultipleObjectMixin):
    model = KanjiLevel
    paginate_by = 10
    def get_context_data(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.kanjilesson_set.filter(name__icontains=name)
        else:
            object_list = self.object.kanjilesson_set.all()
        context = super(KanjiLevelDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context

class Kanji_lesson_detail(LoginRequiredMixin, generic.DetailView, MultipleObjectMixin):
    model = KanjiLesson
    paginate_by = 20

    def get_success_url(self):
        print("12131231313123123")
        return reverse('kanji-detail', kwargs={'pk': self.object.pk,'kanji_lesson_id':self.object.kanji_level.id})
        
        

    def get_context_data(self, **kwargs):
        lesson = self.get_object()
        print(self.object)
        object_list = Kanji.objects.filter(kanji_lesson=lesson)
        context = super(Kanji_lesson_detail, self).get_context_data(object_list=object_list, **kwargs)
        # tests = lesson.test_set.all()
        # user_test_list = []
        # marked_word_list = []
        # new_list = []
        # tested_list = []
        # for test in tests:
        #     if UserTest.objects.filter(user=self.request.user.id, test=test.id).first():
        #         user_test_list.append(UserTest.objects.filter(user=self.request.user.id, test=test.id).first())
        #         tested_list.append(test)

        # for word in object_list:
        #     if not UserWord.objects.filter(user=self.request.user.id, word=word.id).first():
        #         new_list.append(word)
        #     else:
        #         marked_word_list.append(word)
        # context['user_test_list'] = user_test_list
        # context['tested_list'] = tested_list
        # context['marked_word_list'] = marked_word_list
        # context['new_list'] = new_list
        # if UserTest.objects.filter(user=self.request.user, test=lesson.test_set.first.id):
        #     context['my_test'] = UserTest.objects.filter(user=self.request.user, test=lesson.test).first()
        return context
class ListeningLevelListView(generic.ListView):
    model = ListeningLevel
    paginate_by = 3

    def get_queryset(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.model.objects.filter(name__icontains=name)
        else:
            object_list = self.model.objects.filter()
        return object_list

class ListeningLevelDetailView(generic.DetailView, MultipleObjectMixin):
    model = ListeningLevel
    paginate_by = 10
    def get_context_data(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.listeninglesson_set.filter(name__icontains=name)
        else:
            object_list = self.object.listeninglesson_set.all()
        context = super(ListeningLevelDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context

class Listening_lesson_detail(LoginRequiredMixin, generic.DetailView, MultipleObjectMixin):
    model = ListeningLesson
    paginate_by = 20

    def get_success_url(self):
        print("12131231313123123")
        return reverse('listening-detail', kwargs={'pk': self.object.pk,'listening_lesson_id':self.object.listening_level.id})
        
        

    def get_context_data(self, **kwargs):
        lesson = self.get_object()
        print(self.object)
        object_list = Listening.objects.filter(listening_lesson=lesson)
        context = super(Listening_lesson_detail, self).get_context_data(object_list=object_list, **kwargs)
        return context
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        data = {}
        lesson = ListeningLesson.objects.get(id=self.kwargs['pk'])
        print(lesson)
        listening = Listening.objects.filter(listening_lesson=lesson).first()
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            question_id = key.split('-')[1]
            choice_id = request.POST.get(key)
            data[question_id] = choice_id
        perform_listening(request.user, data, listening)
        return redirect(reverse('show_results_listening', args=(listening.id,)))
class ReadingLevelListView(generic.ListView):
    model = ReadingLevel
    paginate_by = 3

    def get_queryset(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.model.objects.filter(name__icontains=name)
        else:
            object_list = self.model.objects.filter()
        return object_list

class ReadingLevelDetailView(generic.DetailView, MultipleObjectMixin):
    model = ReadingLevel
    paginate_by = 10
    def get_context_data(self, **kwargs):
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.readinglesson_set.filter(name__icontains=name)
        else:
            object_list = self.object.readinglesson_set.all()
        context = super(ReadingLevelDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context

class Reading_lesson_detail(LoginRequiredMixin, generic.DetailView, MultipleObjectMixin):
    model = ReadingLesson
    paginate_by = 20

    def get_success_url(self):
        print("12131231313123123")
        return reverse('reading-detail', kwargs={'pk': self.object.pk,'reading_lesson_id':self.object.reading_level.id})
        
    

    def get_context_data(self, **kwargs):
        lesson = self.get_object()
        object_list = Reading.objects.filter(reading_lesson=lesson)
        context = super(Reading_lesson_detail, self).get_context_data(object_list=object_list, **kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        data = {}
        lesson = ReadingLesson.objects.get(id=self.kwargs['pk'])
        print(lesson)
        reading = Reading.objects.filter(reading_lesson=lesson).first()
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            question_id = key.split('-')[1]
            choice_id = request.POST.get(key)
            data[question_id] = choice_id
        perform_reading(request.user, data, reading)
        return redirect(reverse('show_results_reading', args=(reading.id,)))
        
def perform_reading(user, data, reading):
    with transaction.atomic():
        UserAnswer.objects.filter(user=user, question__reading=reading).delete()
        for question_id, choice_id in data.items():
            question = Question.objects.get(id=question_id)
            choice_id = int(choice_id)
            if choice_id not in question.choice_set.values_list('id', flat=True):
                raise SuspiciousOperation('Choice is not valid for this question')
            UserAnswer.objects.create(user=user,
                                      question=question,
                                      choice_id=choice_id, )


def calculate_score_reading(user, reading):
    questions = Question.objects.filter(reading=reading)
    correct_choices = UserAnswer.objects.filter(
        user=user,
        question__reading=reading,
        choice__correct=True
    )
    score = TestResult(user=user, reading=reading, correct_answer_num=correct_choices.count())
    score.save()
    return correct_choices.count()



def show_form_correct_reading(request, pk):
    is_authenticated(request)
    reading = Reading.objects.get(id=pk)
    
    choices = UserAnswer.objects.filter(
        user=request.user,
        question__reading=reading,
    )
    listchoices = []
    for choices1 in choices:
        listchoices.append(choices1.choice)
    context = {
        'test': reading,
        'score': calculate_score_reading(request.user, reading),
        'choices': listchoices,
    }
    UserAnswer.objects.filter(user=request.user, question__reading=reading).delete()
    return render(request, 'gogoedu/show_results_reading.html', context)

def perform_listening(user, data, listening):
    with transaction.atomic():
        UserAnswer.objects.filter(user=user, question__listening=listening).delete()
        for question_id, choice_id in data.items():
            question = Question.objects.get(id=question_id)
            choice_id = int(choice_id)
            if choice_id not in question.choice_set.values_list('id', flat=True):
                raise SuspiciousOperation('Choice is not valid for this question')
            UserAnswer.objects.create(user=user,
                                      question=question,
                                      choice_id=choice_id, )


def calculate_score_listening(user, listening):
    questions = Question.objects.filter(listening=listening)
    correct_choices = UserAnswer.objects.filter(
        user=user,
        question__listening=listening,
        choice__correct=True
    )
    score = TestResult(user=user, listening=listening, correct_answer_num=correct_choices.count())
    score.save()
    return correct_choices.count()



def show_form_correct_listening(request, pk):
    is_authenticated(request)
    listening = Listening.objects.get(id=pk)
    
    choices = UserAnswer.objects.filter(
        user=request.user,
        question__listening=listening,
    )
    listchoices = []
    for choices1 in choices:
        listchoices.append(choices1.choice)
    context = {
        'test': listening,
        'score': calculate_score_listening(request.user, listening),
        'choices': listchoices,
    }
    UserAnswer.objects.filter(user=request.user, question__listening=listening).delete()
    return render(request, 'gogoedu/show_results_listening.html', context)
class ChartData(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, format=None):
        today = datetime.date.today()
        sw1 = today - datetime.timedelta(6)
        
        sw2=today-datetime.timedelta(5)
        sw3=today-datetime.timedelta(4)
        sw4=today-datetime.timedelta(3)
        sw5=today-datetime.timedelta(2)
        sw6=today-datetime.timedelta(1)
        # top_points = myUser.objects.annotate(average_correct=Avg('testresult__correct_answer_num', distinct=True),num_tests=Count('testresult', distinct=True),num_words=Count('userword', distinct=True),num_badges=Count('interface__badge',filter=Q(interface__badge__acquired=True, interface__badge__revoked=False), distinct=True))
        ltoday=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=datetime.date.today()),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=datetime.date.today(),testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=datetime.date.today(),testresult__listening__isnull=False),distinct=True)).first()
        l6=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw6),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__listening__isnull=False),distinct=True)).first()
        l5=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw5),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw5,testresult__listening__isnull=False),distinct=True)).first()
        l4=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw4),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw4,testresult__listening__isnull=False),distinct=True)).first()
        l3=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw3),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw3,testresult__listening__isnull=False),distinct=True)).first()
        l2=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw2),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw2,testresult__listening__isnull=False),distinct=True)).first()
        l1=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw1),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw1,testresult__listening__isnull=False),distinct=True)).first()
        learned_today_test = UserWord.objects.filter(user=request.GET.get('user_id',),date__date=datetime.date.today()- datetime.timedelta(1)).count()
        print()
        labels = [sw1,sw2,sw3,sw4,sw5,sw6,today]
        data_set=[l1.num_vocab,l2.num_vocab,l3.num_vocab,l4.num_vocab,l5.num_vocab,l6.num_vocab,ltoday.num_vocab]
        datar=[l1.num_reading,l2.num_reading,l3.num_reading,l4.num_reading,l5.num_reading,l6.num_reading,ltoday.num_reading]
        datal=[l1.num_listening,l2.num_listening,l3.num_listening,l4.num_listening,l5.num_listening,l6.num_listening,ltoday.num_listening]
        data={
            "labels":labels,
            "data":data_set,
            "datar":datar,
            "datal":datal,
        }
        return Response(data)
