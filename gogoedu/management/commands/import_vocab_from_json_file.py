"""
Import json data from JSON file to Datababse
"""
import os
import json
from gogoedu.models import Catagory,Lesson,Word
from django.core.management import BaseCommand
from elearning.settings import BASE_DIR


class Command(BaseCommand):
    def import_vocab_from_file(self):
        data_folder = os.path.join(BASE_DIR, 'gogoedu', 'static/json_file/vocab')
        for data_file in os.listdir(data_folder):
            with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                data = json.loads(data_file.read())
                catagory,createdCatagory=Catagory.objects.get_or_create(name="Kanji Genki")
                for data_object in data:
                    kana = data_object.get('Kana', None)
                    kanji = data_object.get('Kanji', None)
                    lesson = data_object.get('Lesson', None)
                    mean = data_object.get('Meaning', None)
                    try:
                        lesson, created_lesson = Lesson.objects.get_or_create(
                            name = lesson,
                            catagory = catagory,
                        )
                        if created_lesson:
                            lesson.save()
                            display_format = "\nLesson, {}, has been saved."
                            print(display_format.format(lesson))
                        word, created_word = Word.objects.get_or_create(
                            word=kana,
                            mean=mean,
                            kanji=kanji,
                            catagory=catagory,
                        )
                        word.lesson.add(lesson)
                        if created_word:
                            word.save()
                            display_format = "\nWord, {}, has been saved."
                            print(display_format.format(word))
                    except Exception as ex:
                        print(str(ex))
                        msg = "\n\nSomething went wrong saving this Word: {}\n{}".format(kana, str(ex))
                        print(msg)
                    


    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_vocab_from_file()