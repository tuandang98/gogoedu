from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import GrammarLevel, myUser
from .models import Catagory, Lesson, Word, Test, Question, Choice, UserTest, UserWord,Mission, TestResult,UserKanji,GrammarLevel,GrammarMean,GrammarLesson,Example,Grammar,ExampleKanji,KanjiLevel,KanjiLesson,Kanji,ReadingLevel,ReadingLesson,Reading,Listening,ListeningLesson,ListeningLevel
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

class GrammarLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(GrammarLevel, GrammarLevelAdmin)

class KanjiLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(KanjiLevel, KanjiLevelAdmin)

class ReadingLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(ReadingLevel, ReadingLevelAdmin)

class ListeningLevelAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(ListeningLevel, ListeningLevelAdmin)

class WordInline(NestedStackedInline):
    model = Word.lesson.through
    extra = 1


class GrammarLessonAdmin(NestedModelAdmin):
    list_display = ('name', 'grammar_level')
    list_filter = ('grammar_level',)
    search_fields = ['name']
    

admin.site.register(GrammarLesson, GrammarLessonAdmin)

class KanjiLessonAdmin(NestedModelAdmin):
    list_display = ('name', 'kanji_level')
    list_filter = ('kanji_level',)
    search_fields = ['name']
    

admin.site.register(KanjiLesson, KanjiLessonAdmin)

class ReadingLessonAdmin(NestedModelAdmin):
    list_display = ('name', 'reading_level')
    list_filter = ('reading_level',)
    search_fields = ['name']
    

admin.site.register(ReadingLesson, ReadingLessonAdmin)

class ListeningLessonAdmin(NestedModelAdmin):
    list_display = ('name', 'listening_level')
    list_filter = ('listening_level',)
    search_fields = ['name']
    

admin.site.register(ListeningLesson, ListeningLessonAdmin)

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


class ExampleInline(NestedStackedInline):
    model = Example
    extra = 1


class MeanInline(NestedStackedInline):
    model = GrammarMean
    extra = 1
    show_change_link = True
    inlines = [ExampleInline,]


class GrammarAdmin(NestedModelAdmin):
    list_display = ('name', 'connect','grammar_lesson')
    list_filter = ('name', 'grammar_lesson' )
    search_fields = ['name']
    inlines = [MeanInline,]


admin.site.register(Grammar, GrammarAdmin)


class MeanAdmin(NestedModelAdmin):
    list_display = ('mean', 'grammar')
    search_fields = ['grammar']
    inlines = [ExampleInline,]


admin.site.register(GrammarMean, MeanAdmin)


class ExampleAdmin(admin.ModelAdmin):
    list_display = ('example', 'grammar_mean')
    list_filter = ('example', 'grammar_mean')
    search_fields = ['example']


class ExampleKanjiInline(NestedStackedInline):
    model = ExampleKanji
    extra = 1
    show_change_link = True


class KanjiAdmin(NestedModelAdmin):
    list_display = ('kanji','kanji_lesson', 'reading','definition')
    list_filter = ('kanji', 'kanji_lesson' )
    search_fields = ['kanji','kanji_lesson']
    inlines = [ExampleKanjiInline,]


admin.site.register(Kanji, KanjiAdmin)


class ExampleKanjiAdmin(admin.ModelAdmin):
    list_display = ('example','kanji', 'reading','definition')
    list_filter = ('example', 'kanji')
    search_fields = ['example']

admin.site.register(ExampleKanji, ExampleKanjiAdmin)

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

class ReadingAdmin(NestedModelAdmin):
    list_display = ('mondai', 'text', 'reading_lesson' )
    list_filter = ('reading_lesson', )
    search_fields = ['reading_lesson']
    inlines = [QuestionInline,]


admin.site.register(Reading, ReadingAdmin)

class ListeningAdmin(NestedModelAdmin):
    list_display = ('text', 'file', 'listening_lesson' )
    list_filter = ('listening_lesson', )
    search_fields = ['listening_lesson']
    inlines = [QuestionInline,]


admin.site.register(Listening, ListeningAdmin)

class QuestionAdmin(NestedModelAdmin):
    list_display = ('test','reading', 'listening','question_text')
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
admin.site.register(UserKanji)
class TestResultAdmin(NestedModelAdmin):
    list_display = ('user', 'date')
    list_filter = ('date',)
    search_fields = ['date']
admin.site.register(TestResult, TestResultAdmin)    
admin.site.register(GamificationInterface)
admin.site.register(Badge)
admin.site.register(BadgeDefinition)
admin.site.register(Category)
admin.site.register(PointChange)
admin.site.register(Unlockable)
admin.site.register(UnlockableDefinition)
admin.site.register(Progression)

class MissionAdmin(NestedModelAdmin):
    list_display = ('user', 'name','updated_at')
    list_filter = ('user',)
    search_fields = ['user']
admin.site.register(Mission, MissionAdmin)   
