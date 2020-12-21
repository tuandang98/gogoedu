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

from .forms import RegisterForm, UserUpdateForm
from gogoedu.models import myUser, Lesson, Word, Catagory, Test, UserTest, Question, Choice, UserAnswer, UserWord, \
    TestResult

from PIL import Image

from django.shortcuts import get_object_or_404
from django.db import transaction

from django.core.exceptions import PermissionDenied
from background_task import background
from datetime import datetime, timedelta

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
    paginate_by = 2

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
    paginate_by = 1

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
    list_tested = UserTest.objects.filter(user=request.user.id)

    paginator1 = Paginator(list_tested, 5)
    page = request.GET.get('page', 1)
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

    paginator3 = Paginator(list_learned, 1)
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
               'total_tested': list_tested
               }
    return HttpResponse(template.render(context, request))


def contact_view(request):
    return render(request, 'contact.html')


def about_view(request):
    return render(request, 'about.html')


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
