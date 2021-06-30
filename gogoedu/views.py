from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.mail.backends import console
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, response
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
from django.contrib.auth import login, authenticate,update_session_auth_hash
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
from django.contrib.auth.forms import PasswordChangeForm
from gogoedu.models import Grammar, GrammarLevel, myUser, Lesson, Word, Catagory, Test, UserTest, Question, Choice, UserAnswer, UserWord, \
    TestResult,GrammarLevel,GrammarLesson,GrammarMean,UserGrammar,Example,KanjiLesson,KanjiLevel,Kanji,Reading,ReadingLesson,ReadingLevel,ListeningLevel,ListeningLesson,Listening,UserKanji,Mission,todo
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer,StaticHTMLRenderer
from PIL import Image
from notifications.signals import notify
from django.shortcuts import get_object_or_404
from django.db import transaction

from django.core.exceptions import PermissionDenied
from background_task import background

from django.db.models import Avg, Count, Min, Sum, Q,Max,F,FloatField
import random 
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView, RedirectView
from django_gamification.models import Badge,BadgeDefinition, Category, UnlockableDefinition, GamificationInterface,PointChange
from datetime import timedelta
import datetime

def index(request):
    return render(request, 'base_generic.html')


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
        user = self.get_object()
        listcata = []
        listkanji = []
        listgrammar = []
        object_list = UserWord.objects.filter(user=user.id)
        result = (UserWord.objects.values('word__catagory')
                    .annotate(dcount=Count('word'))
                    .filter(word__catagory__isnull=False,user=user.id)
                    .order_by('-dcount')
                )
        for r in result:
            word = Word.objects.filter(catagory=r.get('word__catagory')).count()
            catagory = Catagory.objects.get(id=r.get('word__catagory'))
            percent=r.get('dcount')/word
            
            listcata.append(catagory)
            listcata.append(round(percent*100))
        result2 = (UserKanji.objects.values('kanji__kanji_lesson__kanji_level')
                    .annotate(dcount=Count('kanji'))
                    .filter(user=user.id)
                    .order_by('-dcount')
                )
        for r in result2:
            kanji = Kanji.objects.filter(kanji_lesson__kanji_level=r.get('kanji__kanji_lesson__kanji_level')).count()
            catagory = KanjiLevel.objects.get(id=r.get('kanji__kanji_lesson__kanji_level'))
            percent=r.get('dcount')/kanji
            
            listkanji.append(catagory)
            listkanji.append(round(percent*100))

        result3 = (UserGrammar.objects.values('grammar__grammar_lesson__grammar_level')
                    .annotate(dcount=Count('grammar'))
                    .filter(user=user.id)
                    .order_by('-dcount')
                )
        for r in result3:
            grammar = Grammar.objects.filter(grammar_lesson__grammar_level=r.get('grammar__grammar_lesson__grammar_level')).count()
            catagory = GrammarLevel.objects.get(id=r.get('grammar__grammar_lesson__grammar_level'))
            percent=r.get('dcount')/grammar
            
            listgrammar.append(catagory)
            listgrammar.append(round(percent*100))
        
        context = super(Profile, self).get_context_data(object_list=object_list, **kwargs)
        context["listcata"] =listcata 
        context["listkanji"] =listkanji
        context["listgrammar"] =listgrammar
        
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
        mission= Mission.objects.create(
                name="DailyLogin",
                user=user,
                description='Daily Login Points',
                process=1,
                target=6,
                point=50,
                )
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
    paginate_by = 5

    def get_context_data(self, **kwargs):
        user = myUser.objects.filter(id=self.request.user.id).first()
        
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.lesson_set.filter(name__icontains=name).annotate(wcount=Count('word', distinct=True,output_field=FloatField()),lcount=Count('word',filter=Q(word__userword__user=user), distinct=True,output_field=FloatField())).annotate(percent=F('lcount') / F('wcount')*100)
        else:
            object_list = self.object.lesson_set.all().annotate(wcount=Count('word', distinct=True,output_field=FloatField()),lcount=Count('word',filter=Q(word__userword__user=user), distinct=True,output_field=FloatField())).annotate(percent=F('lcount') / F('wcount')*100)
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
               
                return redirect('profile-detail', pk)
        else:
            form = UserUpdateForm(instance=user)

        return render(request, 'gogoedu/myuser_update.html', {'form': form, 'avatar': avatar})
    else:
        return redirect('index')
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'gogoedu/change_password.html', {
        'form': form
    })

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
        
        if test.lesson is not None:
            return redirect('lesson-detail', test.lesson.id)
        if test.kanji_lesson is not None:
            return redirect('kanji-detail', test.kanji_lesson.id ,test.kanji_lesson.kanji_level.id)
        if test.grammar_lesson is not None:
            return redirect('grammar-detail', test.grammar_lesson.id ,test.grammar_lesson.grammar_level.id)


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
class MarkLearnedKanji(generic.View):

    def post(self, request, pk, wordid):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        print(wordid)
        user_word = UserKanji()
        user_word.user = myUser.objects.get(id=request.user.id)
        user_word.kanji = Kanji.objects.get(id=wordid)
        if not UserKanji.objects.filter(user=request.user.id, kanji=wordid).first():
            user_word.save()
            learned = True
        else:
            UserKanji.objects.filter(user=request.user.id, kanji=wordid).delete()
            learned = False
        return JsonResponse({'word': model_to_dict(user_word), 'learned': learned}, status=200)

class MarkLearnedGrammar(generic.View):

    def post(self, request, pk, wordid):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        user_word = UserGrammar()
        user_word.user = myUser.objects.get(id=request.user.id)
        user_word.grammar = Grammar.objects.get(id=wordid)
        if not UserGrammar.objects.filter(user=request.user.id, grammar=wordid).first():
            user_word.save()
            learned = True
        else:
            UserGrammar.objects.filter(user=request.user.id, grammar=wordid).delete()
            learned = False
        return JsonResponse({'word': model_to_dict(user_word), 'learned': learned}, status=200)
def summary_detail_view(request):
    is_authenticated(request)
    template = loader.get_template('gogoedu/summary.html')
    
    list_word_learned_date = UserWord.objects.filter(user=request.user.id).values_list('date__date',flat=True).order_by('date__date').distinct()
    list_kanji_learned_date = UserKanji.objects.filter(user=request.user.id).values_list('date__date',flat=True).order_by('date__date').distinct()
    list_grammar_learned_date = UserGrammar.objects.filter(user=request.user.id).values_list('date__date',flat=True).order_by('date__date').distinct()
    listdate = list(list_word_learned_date)+list(list_kanji_learned_date)+list(list_grammar_learned_date)
    d = {}
    my_set = set(listdate)
    my_new_list = list(my_set)
   
    my_new_list.sort(key=lambda x: x, reverse=True)
    for list1 in my_new_list:
        dateword=UserWord.objects.filter(user=request.user.id,date__date=list1)
        datekanji=UserKanji.objects.filter(user=request.user.id,date__date=list1)
        dategrammar=UserGrammar.objects.filter(user=request.user.id,date__date=list1)
        d.update({list1:[dateword,datekanji,dategrammar]})
    search = request.GET.get('search')
    
    try:
        if search:
            searchdate=datetime.datetime.strptime(search, "%Y-%m-%d").date()
            if searchdate in d:
                listd=d[searchdate]
                d={
                    searchdate:listd
                }
    except ValueError:
        pass
       
        # dateword=UserWord.objects.filter(user=request.user.id,date__date__icontains=search)
        # datekanji=UserKanji.objects.filter(user=request.user.id,date__date__icontains=search)
        # dategrammar=UserGrammar.objects.filter(user=request.user.id,date__date__icontains=search)
        
  
  
    list_tested = TestResult.objects.filter(user=request.user.id).order_by('-date')
    test = request.GET.get('test')
    try:
        if test:
            searchdate=datetime.datetime.strptime(test, "%Y-%m-%d").date()
            list_tested = TestResult.objects.filter(user=request.user.id,date__icontains=searchdate)
    except ValueError:
        pass
       
    page = request.GET.get('page', 1)
    paginator1 = Paginator(list_tested, 5)
    
    try:
        tested_paged = paginator1.page(page)
    except PageNotAnInteger:
        tested_paged = paginator1.page(1)
    except EmptyPage:
        tested_paged = paginator1.page(paginator1.num_pages)

  
   
    context = {"list_tested": tested_paged,
               'total_tested': list_tested,
               'dict_date':d,
               }
    return HttpResponse(template.render(context, request))


def flashcard_view(request):
    lesson_query_set = Lesson.objects.all().order_by('catagory')
    page = request.GET.get('page', 1)
    paginator1 = Paginator(lesson_query_set, 5)
    
    try:
        paged = paginator1.page(page)
    except PageNotAnInteger:
        paged = paginator1.page(1)
    except EmptyPage:
        paged = paginator1.page(paginator1.num_pages)
    context = {"list_lesson": paged,}  
    return render(request, 'flashcard.html', context)

def view_card_set(request, pk):
    lesson = get_object_or_404(Lesson, id = pk)
    word_list = lesson.word_set.all()
    card_object = word_list.first()	   
    page = request.GET.get('page', 1)
    paginator = Paginator(word_list, 1)
    marked_word_list=[]
    new_list=[]
    for word in word_list:
            if not UserWord.objects.filter(user=request.user.id, word=word.id).first():
                new_list.append(word)
            else:
                marked_word_list.append(word)
    try:
        word_list_paged = paginator.page(page)
    except PageNotAnInteger:
        word_list_paged = paginator.page(1)
    except EmptyPage:
        word_list_paged = paginator.page(paginator.num_pages)

    context = {'lesson': lesson, 'card_object': word_list_paged,'marked_word_list':marked_word_list}
    return render(request, 'gogoedu/view_cards.html', context)

def viewflashcard(request,pk):
    lesson = get_object_or_404(Lesson, id = pk)
    word_list = lesson.word_set.all() 
    page = request.GET.get('page', 1)
    paginator = Paginator(word_list, 1)
    marked_word_list=[]
    new_list=[]
    for word in word_list:
            if not UserWord.objects.filter(user=request.user.id, word=word.id).first():
                new_list.append(word)
            else:
                marked_word_list.append(word)
    try:
        word_list_paged = paginator.page(page)
    except PageNotAnInteger:
        word_list_paged = paginator.page(1)
    except EmptyPage:
        word_list_paged = paginator.page(paginator.num_pages)

    context = {'lesson': lesson, 'card_object': word_list_paged,'marked_word_list':marked_word_list}
    return render(request, 'gogoedu/view_cards.html', context)

def viewkanjiflash(request,pk):
    lesson = get_object_or_404(KanjiLesson, id = pk)
    word_list = lesson.kanji_set.all() 
    page = request.GET.get('page', 1)
    paginator = Paginator(word_list, 1)
    marked_word_list=[]
    new_list=[]
    for word in word_list:
            if not UserKanji.objects.filter(user=request.user.id, kanji=word.id).first():
                new_list.append(word)
            else:
                marked_word_list.append(word)
    try:
        word_list_paged = paginator.page(page)
    except PageNotAnInteger:
        word_list_paged = paginator.page(1)
    except EmptyPage:
        word_list_paged = paginator.page(paginator.num_pages)

    context = {'lesson': lesson, 'card_object': word_list_paged,'marked_word_list':marked_word_list}
    return render(request, 'gogoedu/view_cards_kanji.html', context)

def leaderboard_view(request):
    template = loader.get_template('leaderboard.html')
    top_points = myUser.objects.annotate(average_correct=Avg('testresult__correct_answer_num', distinct=True),num_tests=Count('testresult', distinct=True),num_words=Count('userword', distinct=True),num_badges=Count('interface__badge',filter=Q(interface__badge__acquired=True, interface__badge__revoked=False), distinct=True)).exclude(interface=None)
    

    context = {"top_points": sorted(top_points,  key=lambda p: p.interface.points,reverse=True)[:3],
                
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

def kanjiflashcard_test(request, pk):
    template = loader.get_template('gogoedu/flashcard_test.html')
    lesson = get_object_or_404(KanjiLesson, id = pk)
    word_list = lesson.kanji_set.all()
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
    
    kq=calculate_score(user, test)
    print(kq)
    UserAnswer.objects.filter(user=user, question__test=test).delete()
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

def alphabet(request):
    return render(request, 'gogoedu/alphabet.html')

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
        new_list = []
        marked_word_list = []
        tests = lesson.test_set.all()
        user_test_list = []
        tested_list = []
        for test in tests:
            if UserTest.objects.filter(user=self.request.user.id, test=test.id).first():
                user_test_list.append(UserTest.objects.filter(user=self.request.user.id, test=test.id).first())
                tested_list.append(test)
        for word in object_list:
            if not UserGrammar.objects.filter(user=self.request.user.id, grammar=word.id).first():
                new_list.append(word)
            else:
                marked_word_list.append(word)
        context['marked_word_list'] = marked_word_list
        context['new_list'] = new_list
        context['user_test_list'] = user_test_list
        context['tested_list'] = tested_list
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
    paginate_by = 5
    def get_context_data(self, **kwargs):
        user = myUser.objects.filter(id=self.request.user.id).first()
        try:
            name = self.request.GET.get('name', )
        except:
            name = ''
        if name:
            object_list = self.object.kanjilesson_set.filter(name__icontains=name).annotate(wcount=Count('kanji', distinct=True,output_field=FloatField()),lcount=Count('kanji',filter=Q(kanji__userkanji__user=user), distinct=True,output_field=FloatField())).annotate(percent=F('lcount') / F('wcount')*100)
        else:
            object_list = self.object.kanjilesson_set.all().annotate(wcount=Count('kanji', distinct=True,output_field=FloatField()),lcount=Count('kanji',filter=Q(kanji__userkanji__user=user), distinct=True,output_field=FloatField())).annotate(percent=F('lcount') / F('wcount')*100)
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
        new_list = []
        marked_word_list = []
        tests = lesson.test_set.all()
        user_test_list = []
        tested_list = []
        for test in tests:
            if UserTest.objects.filter(user=self.request.user.id, test=test.id).first():
                user_test_list.append(UserTest.objects.filter(user=self.request.user.id, test=test.id).first())
                tested_list.append(test)
        for word in object_list:
            if not UserKanji.objects.filter(user=self.request.user.id, kanji=word.id).first():
                new_list.append(word)
            else:
                marked_word_list.append(word)
        context['marked_word_list'] = marked_word_list
        context['new_list'] = new_list
        context['user_test_list'] = user_test_list
        context['tested_list'] = tested_list
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
        ltoday=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=datetime.date.today()),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=today),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=today),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=datetime.date.today(),testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=datetime.date.today(),testresult__listening__isnull=False),distinct=True)).first()
        l6=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw6),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=sw6),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=sw6),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw6,testresult__listening__isnull=False),distinct=True)).first()
        l5=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw5),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=sw5),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=sw5),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw5,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw5,testresult__listening__isnull=False),distinct=True)).first()
        l4=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw4),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=sw4),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=sw4),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw4,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw4,testresult__listening__isnull=False),distinct=True)).first()
        l3=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw3),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=sw3),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=sw3),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw3,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw3,testresult__listening__isnull=False),distinct=True)).first()
        l2=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw2),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=sw2),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=sw2),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw2,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw2,testresult__listening__isnull=False),distinct=True)).first()
        l1=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__date=sw1),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__date=sw1),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__date=sw1),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__date=sw1,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__date=sw1,testresult__listening__isnull=False),distinct=True)).first()
        learned_today_test = UserWord.objects.filter(user=request.GET.get('user_id',),date__date=datetime.date.today()- datetime.timedelta(1)).count()
        current_week= [sw1,today]
        current_week_word=l1.num_vocab+l2.num_vocab+l3.num_vocab+l4.num_vocab+l5.num_vocab+l6.num_vocab+ltoday.num_vocab
        current_week_kanji=l1.num_kanji+l2.num_kanji+l3.num_kanji+l4.num_kanji+l5.num_kanji+l6.num_kanji+ltoday.num_kanji
        current_week_grammar=l1.num_grammar+l2.num_grammar+l3.num_grammar+l4.num_grammar+l5.num_grammar+l6.num_grammar+ltoday.num_grammar
        current_week_listening=l1.num_listening+l2.num_listening+l3.num_listening+l4.num_listening+l5.num_listening+l6.num_listening+ltoday.num_listening
        current_week_reading=l1.num_reading+l2.num_reading+l3.num_reading+l4.num_reading+l5.num_reading+l6.num_reading+ltoday.num_reading

        last_week=[sw1-datetime.timedelta(7),sw1-datetime.timedelta(1)]
        last_week_learned=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__range=last_week),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__range=last_week),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__range=last_week),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__range=last_week,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__range=last_week,testresult__listening__isnull=False),distinct=True)).first()
        last_last_week=[sw1-datetime.timedelta(7)-datetime.timedelta(7),sw1-datetime.timedelta(1)-datetime.timedelta(7)]
        last_last_week_learned=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__range=last_last_week),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__range=last_last_week),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__range=last_last_week),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__range=last_last_week,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__range=last_last_week,testresult__listening__isnull=False),distinct=True)).first()
        last_last_last_week=[sw1-datetime.timedelta(7)-datetime.timedelta(7)-datetime.timedelta(7),sw1-datetime.timedelta(1)-datetime.timedelta(7)-datetime.timedelta(7)]
        last_last_last_week_learned=myUser.objects.filter(id=request.GET.get('user_id',)).annotate(num_vocab=Count('userword',filter=Q(userword__date__range=last_last_last_week),distinct=True),num_kanji=Count('userkanji',filter=Q(userkanji__date__range=last_last_last_week),distinct=True),num_grammar=Count('usergrammar',filter=Q(usergrammar__date__range=last_last_last_week),distinct=True),num_reading=Count('testresult',filter=Q(testresult__date__range=last_last_last_week,testresult__reading__isnull=False),distinct=True),num_listening=Count('testresult',filter=Q(testresult__date__range=last_last_last_week,testresult__listening__isnull=False),distinct=True)).first()
        labels = [sw1,sw2,sw3,sw4,sw5,sw6,today]
        
        data_set=[l1.num_vocab,l2.num_vocab,l3.num_vocab,l4.num_vocab,l5.num_vocab,l6.num_vocab,ltoday.num_vocab]
        datar=[l1.num_reading,l2.num_reading,l3.num_reading,l4.num_reading,l5.num_reading,l6.num_reading,ltoday.num_reading]
        datal=[l1.num_listening,l2.num_listening,l3.num_listening,l4.num_listening,l5.num_listening,l6.num_listening,ltoday.num_listening]
        kanji=[l1.num_kanji,l2.num_kanji,l3.num_kanji,l4.num_kanji,l5.num_kanji,l6.num_kanji,ltoday.num_kanji]
        grammar=[l1.num_grammar,l2.num_grammar,l3.num_grammar,l4.num_grammar,l5.num_grammar,l6.num_grammar,ltoday.num_grammar]

        labels_week=[last_last_last_week,last_last_week,last_week,current_week]
        data_week_w=[last_last_last_week_learned.num_vocab,last_last_week_learned.num_vocab,last_week_learned.num_vocab,current_week_word]
        data_week_r=[last_last_last_week_learned.num_reading,last_last_week_learned.num_reading,last_week_learned.num_reading,current_week_reading]
        data_week_l=[last_last_last_week_learned.num_listening,last_last_week_learned.num_listening,last_week_learned.num_listening,current_week_listening]
        data_week_k=[last_last_last_week_learned.num_kanji,last_last_week_learned.num_kanji,last_week_learned.num_kanji,current_week_kanji]
        data_week_g=[last_last_last_week_learned.num_grammar,last_last_week_learned.num_grammar,last_week_learned.num_grammar,current_week_grammar]
        data={
            "labels":labels,
            "labels_week":labels_week,
            "data":data_set,
            "datan":kanji,
            "datar":datar,
            "datal":datal,
            "datag":grammar,
            "data_week_w":data_week_w,
            "data_week_r":data_week_r,
            "data_week_l":data_week_l,
            "data_week_k":data_week_k,
            "data_week_g":data_week_g,
        }
        return Response(data)

class MissionView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, format=None):
        user=myUser.objects.filter(id=request.GET.get('user_id',)).first()
        dailylogin= Mission.objects.filter(user=user,name="DailyLogin").first()
        missionw = Mission.objects.filter(user=user,type="W").first()
        missionk = Mission.objects.filter(user=user,type="K").first()
        missionr = Mission.objects.filter(user=user,type="R").first()
        missionl = Mission.objects.filter(user=user,type="L").first()
        missiong = Mission.objects.filter(user=user,type="G").first()
        data={
            "point":user.interface.points,
            "word":missionw.name,
            "wordp":round((missionw.process/missionw.target)*100),
            "kanji":missionk.name,
            "kanjip":round((missionk.process/missionk.target)*100),
            "reading":missionr.name,
            "readingp":round((missionr.process/missionr.target)*100),
            "listening":missionl.name,
            "listeningp":round((missionl.process/missionl.target)*100),
            "grammar":missiong.name,
            "grammarp":round((missiong.process/missiong.target)*100),
            "dailylogin":dailylogin.process,
            "dailyloginPoint":dailylogin.point,
            
        }
        return Response(data)
@background(schedule=20)
def reset_daily():
    missionw = Mission.objects.filter(type="W").update(process=0,complete=False)
    missionk = Mission.objects.filter(type="K").update(process=0,complete=False)
    missionr = Mission.objects.filter(type="R").update(process=0,complete=False)
    missionl = Mission.objects.filter(type="L").update(process=0,complete=False)
    missiong = Mission.objects.filter(type="G").update(process=0,complete=False)

class CheckAlphabet(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, format=None):
        user=myUser.objects.filter(id=request.GET.get('user_id',)).first()
        category_learned=Category.objects.filter(
            name='Learned', 
            description='These are the learned badges'
        ).first()
        badge_definition=BadgeDefinition.objects.filter(
                name='Alphabet Finished',
                description='Finished learning the alphabet',
                points=50,
                progression_target=100,
                category=category_learned,
                ).first()
        badge=Badge.objects.filter(
            interface=user.interface,
            category=category_learned,
            badge_definition=badge_definition
        ).first()
        
        if badge.acquired is False:
            badge.progression.progress=badge.progression.target
            badge.increment()
            PointChange.objects.create(amount=badge.point,interface=user.interface)
            badge.save()
            learned=False
        else:
            learned=True
        data={
            "learned":learned,
            
        }
        return Response(data)
def listtest(request):
    test = Test.objects.all()
    context = {"test": test,}  
    return render(request, 'gogoedu/listtest.html', context)
@api_view(('POST',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def message(request):
    is_authenticated(request)
    try:
        if request.method == 'POST':
            sender = myUser.objects.get(username=request.user)
            receiver = myUser.objects.get(username=request.POST.get('username'))
            notify.send(sender, recipient=receiver, verb='Message', description=request.POST.get('message'))
            data={
            "learned":'learned',
            
            }
            return Response(data,template_name='base_generic.html')
        else:
            return HttpResponse("Invalid request")
    except Exception as e:
        print(e)
        return HttpResponse("Please login from admin site for sending messages")


@api_view(('POST',))
@renderer_classes([StaticHTMLRenderer])
def new_todo(request):
    is_authenticated(request)
    if request.method == "POST":
        csrf_token = get_token(request)
        csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
        if request.POST.get('todo-name') and not request.POST.get('todo-name').isspace():
            new=todo.objects.create(user=request.user,name=request.POST.get('todo-name'))
            
            data = '<form class="well" id="markdone'+str(new.id)+'"data-id="'+str(new.id)+'" method="post" enctype="multipart/form-data">'+csrf_token_html+'<h4>'+str(new.name)+'</h4><div>'+str(timezone.now().hour-new.created_at.hour)+' hours ago</div><input type="button" value="Mark as Done &#9996"></form>'
            return Response(data)
        else:
            return Response('')
            
@api_view(('GET',))
@renderer_classes([StaticHTMLRenderer])
def todolist(request):
    is_authenticated(request)
   
    if request.method == 'GET':
        csrf_token = get_token(request)
        csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
        list_todo = todo.objects.filter(user=request.user,status=False)
        data = []
        for new in list_todo:
            data.append('<form class="well" id="markdone'+str(new.id)+'"data-id="'+str(new.id)+'" method="post" enctype="multipart/form-data">'+csrf_token_html+'<h4>'+str(new.name)+'</h4><div>'+str(new.created_at.strftime('%d-%m-%Y %H:%M:%S'))+'</div><input type="button" value="Mark as Done &#9996"></form>')
        return Response(data)
@api_view(('POST',))
@renderer_classes([StaticHTMLRenderer])
def mark_as_done(request, id):
    is_authenticated(request)
    if request.method == 'POST':
        
        obj = todo.objects.get(pk=id)
        obj.status = True
        obj.save()
        list_todo = todo.objects.filter(user=request.user,status=False)
        data = 'ok'
       
        return Response(data)
