"""
Import json data from JSON file to Datababse
"""
import os
import json
from gogoedu.models import ExampleKanji, Kanji,KanjiLesson,KanjiLevel
from django.core.management import BaseCommand
from elearning.settings import BASE_DIR


class Command(BaseCommand):
    def import_kanji_from_file(self):
        data_folder = os.path.join(BASE_DIR, 'gogoedu', 'static/json_file/kanji')
        for data_file in os.listdir(data_folder):
            with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                data = json.loads(data_file.read())
                kanji_level,createdKanjilevel=KanjiLevel.objects.get_or_create(name="Kanji Genki")
                for data_object in data:
                    definition = data_object.get('Definition', None)
                    reading = data_object.get('Reading', None)
                    kanji = data_object.get('Kanji', None)
                    lesson = data_object.get('Lesson', None)
                    example = data_object.get('Examples', None)
                    print(kanji_level)
                    try:
                        kanji_lesson, created_lesson = KanjiLesson.objects.get_or_create(
                            name = lesson,
                            kanji_level = kanji_level,
                        )
                        if created_lesson:
                            kanji_lesson.save()
                            display_format = "\nLesson, {}, has been saved."
                            print(display_format.format(kanji_lesson))
                        kanji, created_kanji = Kanji.objects.get_or_create(
                            definition=definition,
                            reading=reading,
                            kanji=kanji,
                            kanji_lesson=kanji_lesson,
                        )
                        if created_kanji:
                            kanji.save()
                            display_format = "\nKanji, {}, has been saved."
                            print(display_format.format(kanji))
                        try:
                            for example_object in example:
                                definitionExample = example_object.get('Definition', None)
                                readingExample = example_object.get('Reading', None)
                                exampleExample = example_object.get('Example', None)
                                example_kanji, created_example = ExampleKanji.objects.get_or_create(
                                    definition=definitionExample,
                                    reading=readingExample,
                                    example=exampleExample,
                                    kanji=kanji,
                                )
                                if created_example:
                                    example_kanji.save()
                                    display_format = "\nexample, {}, has been saved."
                                    print(display_format.format(example_kanji))
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this example: {}\n{}".format(kanji, str(ex))
                            print(msg)
                    except Exception as ex:
                        print(str(ex))
                        msg = "\n\nSomething went wrong saving this kanji: {}\n{}".format(kanji, str(ex))
                        print(msg)
                    


    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_kanji_from_file()