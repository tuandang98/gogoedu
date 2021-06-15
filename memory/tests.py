from django.test import TestCase

from .models import Game, Image, random_id, Player

class GameTests(TestCase):
    def test_urlid(self):
        game = Game()
        self.assertTrue(game.urlid.isalnum(), 'expected alphanumeric urlid')
    
    def test_new_game(self):
        for i in range(30):
            Image.objects.create(id=i)
        game = Game()
        game.new_game()
        self.assertTrue(game.cards.count(), 'no cards in the game')
        self.assertEqual(game.cards.count() % 2, 0, 'number of cards not equal')

        for card in game.cards.all():
            self.assertEqual(game.cards.filter(image=card.image).count(), 2, 'card is not in pairs')

class PlayerTests(TestCase):
    def test_secretid(self):
        player = Player()
        self.assertTrue(player.secretid.isalnum(), 'expected alphanumeric secretid')



class HelperTests(TestCase):
    def test_random_id(self):
        self.assertEqual(random_id(0), '')
        self.assertEqual(len(random_id(10)), 10)
        self.assertEqual(len(random_id(1)), 1)
        self.assertTrue(random_id(1).isalnum())
        self.assertTrue(random_id(10).isalnum())
