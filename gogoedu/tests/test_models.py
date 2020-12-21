from django.test import TestCase

from gogoedu.models import Test,Lesson,Word


class TestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Test.objects.create(name='Love Shiba', time=20,question_num=20)

    def test_name_label(self):
        test = Test.objects.get(id=1)
        field_label = test._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_lesson_label(self):
        test=Test.objects.get(id=1)
        field_label = test._meta.get_field('lesson').verbose_name
        self.assertEquals(field_label, 'lesson')

    def test_time_label(self):
        test=Test.objects.get(id=1)
        field_label = test._meta.get_field('time').verbose_name
        self.assertEquals(field_label, 'time')

    def test_question_num_label(self):
        test=Test.objects.get(id=1)
        field_label = test._meta.get_field('question_num').verbose_name
        self.assertEquals(field_label, 'question num')

    def test_name_max_length(self):
        test = Test.objects.get(id=1)
        max_length = test._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

    def test_object_name_is_name(self):
        test = Test.objects.get(id=1)
        expected_object_name = f'{test.name}'
        self.assertEquals(expected_object_name, str(test))

    def test_get_absolute_url(self):
        test = Test.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(test.get_absolute_url(), '/gogoedu/test/1')

    def test_get_test_url(self):
        test = Test.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(test.get_absolute_url(), '/gogoedu/test/1')


class TestModelLesson(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Lesson.objects.create(name='Love Shiba',description='alo alo')

    def test_name_label(self):
        lesson = Lesson.objects.get(id=1)
        field_label = lesson._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_catagory_label(self):
        lesson=Lesson.objects.get(id=1)
        field_label = lesson._meta.get_field('catagory').verbose_name
        self.assertEquals(field_label, 'catagory')

    def test_description_label(self):
        lesson=Lesson.objects.get(id=1)
        field_label = lesson._meta.get_field('description').verbose_name
        self.assertEquals(field_label, 'description')

    def test_name_max_length(self):
        lesson = Lesson.objects.get(id=1)
        max_length = lesson._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_object_name_is_name(self):
        lesson = Lesson.objects.get(id=1)
        expected_object_name = f'{lesson.name}'
        self.assertEquals(expected_object_name, str(lesson))

    def test_get_absolute_url(self):
        lesson = Lesson.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(lesson.get_absolute_url(), '/gogoedu/lesson/1')


class WordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Word.objects.create(word='Dolphin', mean='Ca heo', type='V')

    def test_word_label(self):
        word = Word.objects.get(id=1)
        field_label = word._meta.get_field('word').verbose_name
        self.assertEquals(field_label, 'word')

    def test_catagory_label(self):
        word = Word.objects.get(id=1)
        field_label = word._meta.get_field('catagory').verbose_name
        self.assertEquals(field_label, 'catagory')

    def test_mean_label(self):
        word = Word.objects.get(id=1)
        field_label = word._meta.get_field('mean').verbose_name
        self.assertEquals(field_label, 'mean')

    def test_type_label(self):
        word = Word.objects.get(id=1)
        field_label = word._meta.get_field('type').verbose_name
        self.assertEquals(field_label, 'type')

    def test_lesson_label(self):
        word = Word.objects.get(id=1)
        field_label = word._meta.get_field('lesson').verbose_name
        self.assertEquals(field_label, 'lesson')

    def test_word_max_length(self):
        word = Word.objects.get(id=1)
        max_length = word._meta.get_field('word').max_length
        self.assertEquals(max_length, 255)

    def test_mean_max_length(self):
        word = Word.objects.get(id=1)
        max_length = word._meta.get_field('mean').max_length
        self.assertEquals(max_length, 255)

    def test_type_max_length(self):
        word = Word.objects.get(id=1)
        max_length = word._meta.get_field('type').max_length
        self.assertEquals(max_length, 10)

    def test_object_word_is_name(self):
        word = Word.objects.get(id=1)
        expected_object_name = f'{word.word}'
        self.assertEquals(expected_object_name, str(word))
