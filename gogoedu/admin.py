from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import myUser
from .models import Catagory, Lesson, Word, Test, Question, Choice, UserTest, UserWord, TestResult
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django_gamification.models import GamificationInterface,Badge,BadgeDefinition,Category,PointChange,Unlockable,UnlockableDefinition,Progression

# Register your models here.
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff', 'is_active')
    list_filter = ('date_joined', 'is_staff', 'is_active')
    search_fields = ['username', 'email', 'first_name', 'last_name']


admin.site.register(myUser, MyUserAdmin)


class CatagoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(Catagory, CatagoryAdmin)


class WordInline(NestedStackedInline):
    model = Word.lesson.through
    extra = 1


class LessonAdmin(NestedModelAdmin):
    list_display = ('name', 'catagory', 'description')
    list_filter = ('catagory',)
    search_fields = ['name']
    inlines = [WordInline,]


admin.site.register(Lesson, LessonAdmin)


class WordAdmin(admin.ModelAdmin):
    list_display = ('word','catagory','mean', 'type')
    list_filter = ( 'type','lesson','catagory')
    search_fields = ['word']


admin.site.register(Word, WordAdmin)


class ChoiceInline(NestedStackedInline):
    model = Choice
    extra = 1


class QuestionInline(NestedStackedInline):
    model = Question
    extra = 1
    show_change_link = True
    inlines = [ChoiceInline,]


class TestAdmin(NestedModelAdmin):
    list_display = ('question_num', 'name', 'lesson', 'time')
    list_filter = ('name', 'question_num', 'lesson' )
    search_fields = ['name']
    inlines = [QuestionInline,]


admin.site.register(Test, TestAdmin)


class QuestionAdmin(NestedModelAdmin):
    list_display = ('test', 'question_text')
    search_fields = ['question_text']
    inlines = [ChoiceInline,]


admin.site.register(Question, QuestionAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'correct')
    list_filter = ('question', 'correct')
    search_fields = ['choice_text']


admin.site.register(Choice, ChoiceAdmin)


class UserTestAdmin(admin.ModelAdmin):
    list_display = ('user', 'test')
    list_filter = ('user', 'test')
    search_fields = ['user']


admin.site.register(UserTest, UserTestAdmin)


class UserWordAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'memoried')
    list_filter = ('word', 'memoried')
    search_fields = ['user']


admin.site.register(UserWord, UserWordAdmin)
admin.site.register(TestResult)
admin.site.register(GamificationInterface)
admin.site.register(Badge)
admin.site.register(BadgeDefinition)
admin.site.register(Category)
admin.site.register(PointChange)
admin.site.register(Unlockable)
admin.site.register(UnlockableDefinition)
admin.site.register(Progression)

