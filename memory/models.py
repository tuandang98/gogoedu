from django.db import models
from django.urls import reverse
import random
from gogoedu.models import Word,Lesson
def random_id(length):
    """return a random string of given length

    the string is composed of numbers and lowercase letters
    """
    CHARACTERS = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(CHARACTERS) for _ in range(length))

def _default_urlid():
    """provides the default for Game.urlid"""
    return random_id(Game._meta.get_field('urlid').max_length)

def _default_secretid():
    """provides the default for Player.secretid"""
    return random_id(Player._meta.get_field('secretid').max_length)

class Game(models.Model):
    """represent a game"""
    STATUS_WAIT_FOR_PLAYERS = 0
    STATUS_NO_CARD_SHOWN = 1
    STATUS_ONE_CARD_SHOWN = 2
    STATUS_TWO_DIFFERENT_CARDS_SHOWN = 3
    STATUS_TWO_IDENTICAL_CARDS_SHOWN = 4
    STATUS_GAME_ENDED = 5
    STATUS_CHOICES = (
        (STATUS_WAIT_FOR_PLAYERS, 'wait for players'),
        (STATUS_NO_CARD_SHOWN, 'no card shown'),
        (STATUS_ONE_CARD_SHOWN, 'one card shown'),
        (STATUS_TWO_DIFFERENT_CARDS_SHOWN, 'two different cards shown'),
        (STATUS_TWO_IDENTICAL_CARDS_SHOWN, 'two identical cards shown'),
        (STATUS_GAME_ENDED, 'game ended'))
    STATUS_IN_GAME = (STATUS_NO_CARD_SHOWN, STATUS_ONE_CARD_SHOWN, STATUS_TWO_DIFFERENT_CARDS_SHOWN, STATUS_TWO_IDENTICAL_CARDS_SHOWN)
    STATUS_OUT_OF_GAME = (STATUS_WAIT_FOR_PLAYERS, STATUS_GAME_ENDED)
    NUMBER_OF_PAIRS = 6
    
    urlid = models.CharField(max_length=10, unique=True, default=_default_urlid)
    """the id of the game used in urls, should be only known to the players"""

    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_WAIT_FOR_PLAYERS)
    """the status of the game"""

    current_player = models.ForeignKey('Player', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    """the current player, i.e. the player who is currently allowed to perform actions"""

    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.urlid
    
    def new_game(self):
        """reset the cards used in the game

        clears the cards used for the game and sets up random cards in pairs
        """
        query_set1 = random.sample(list(Image.objects.all()), Game.NUMBER_OF_PAIRS)
        query_set2 = random.sample(query_set1, Game.NUMBER_OF_PAIRS)
        
        self.status = Game.STATUS_NO_CARD_SHOWN
        self.players.update(score=0)
        self.current_player = random.choice(self.players.all())
        self.save()
        self.cards.all().delete()
        self.cards.set((Card(image=image,word=image.word) for image in query_set1), bulk=False)
        self.cards.set((Card(image=image,word=image.word.mean) for image in query_set2), bulk=False)

    def show_card(self, card):
        assert card.game == self
        if self.status == Game.STATUS_NO_CARD_SHOWN:
            assert card.status == Card.STATUS_BACKSIDE
            card.show()
            self.status = Game.STATUS_ONE_CARD_SHOWN
            self.save()
            card.save()
        elif self.status == Game.STATUS_ONE_CARD_SHOWN:
            first_card = self.cards.get(status=Card.STATUS_FRONTSIDE)
            assert card.status == Card.STATUS_BACKSIDE
            assert not first_card == card
            card.show()
            if card.image == first_card.image:
                self.current_player.score += 1
                self.current_player.save()
                self.status = Game.STATUS_TWO_IDENTICAL_CARDS_SHOWN
            else:
                self.status = Game.STATUS_TWO_DIFFERENT_CARDS_SHOWN
                self.current_player = self.players.exclude(id=self.current_player.id).get()
            self.save()
            card.save()
        elif self.status == Game.STATUS_TWO_DIFFERENT_CARDS_SHOWN:
            self.cards.filter(status=Card.STATUS_FRONTSIDE).update(status=Card.STATUS_BACKSIDE)
            card.show()
            self.status = Game.STATUS_ONE_CARD_SHOWN
            self.save()
            card.save()
        elif self.status == Game.STATUS_TWO_IDENTICAL_CARDS_SHOWN:
            self.cards.filter(status=Card.STATUS_FRONTSIDE).update(status=Card.STATUS_REMOVED)
            if self.cards.filter(status=Card.STATUS_BACKSIDE).count() > 0:
                if card.status == Card.STATUS_BACKSIDE:
                    card.show()
                    self.status = Game.STATUS_ONE_CARD_SHOWN
                    self.save()
                    card.save()
                else:
                    self.status = Game.STATUS_NO_CARD_SHOWN
            else:
                self.cards.update(status=Card.STATUS_FRONTSIDE)
                self.status = Game.STATUS_GAME_ENDED
                self.save()
        else:
            assert False, 'illegal game status for show_card()'


    def message(self):
        if self.status == Game.STATUS_GAME_ENDED:
            highscore = max(player.score for player in self.players.all())
            winners = self.players.filter(score=highscore)
            if winners.count() > 1:
                return 'The match ended in a tie.'
            else:
                return '%s has won' % winners.get()
        elif self.status == Game.STATUS_WAIT_FOR_PLAYERS:
            return 'Please wait for the other player'
        elif self.status in Game.STATUS_IN_GAME:
            return 'It is %s\'s turn.' % self.current_player

    def has_ended(self):
        return self.status == Game.STATUS_GAME_ENDED

    def get_absolute_url(self):
        return reverse('memory:game', args=[self.urlid])

class Player(models.Model):
    secretid = models.CharField(max_length=10, unique=True, default=_default_secretid)
    """the secret id for identifying the player"""

    name = models.CharField(max_length=30)
    """name or nickname of the player"""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    """the game in which this player is participating"""

    score = models.IntegerField(default=0)
    """the score in the current game"""

    def __str__(self):
        return self.name
    
    def is_current_player(self):
        return self.game.current_player == self
    
    def should_refresh(self):
        if self.game.status in Game.STATUS_IN_GAME:
            return not self.is_current_player()
        else:
            return True

    def can_act(self):
        if self.game.status in Game.STATUS_IN_GAME:
            return self.is_current_player()
        else:
            return True

class Image(models.Model):
    """represent an image which appears on the front of the card"""
    offset_x = models.IntegerField()
    """the offset of the image in the image map"""

    offset_y = models.IntegerField()
    """the offset of the image in the image map"""
    word = models.ForeignKey(Word,on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return 'Image%d' % self.id

class Card(models.Model):
    """represent a card in a game"""
    STATUS_BACKSIDE = 0
    STATUS_FRONTSIDE = 1
    STATUS_REMOVED = 2
    STATUS_CHOICES = (
        (STATUS_BACKSIDE, 'backside'),
        (STATUS_FRONTSIDE, 'frontside'),
        (STATUS_REMOVED, 'removed'))


    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='cards')
    """the game in which this card is used"""

    image = models.ForeignKey(Image, on_delete=models.PROTECT, related_name='+')
    """the image on the front of the card"""
    
    word = models.CharField(max_length=255,null=True,blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_BACKSIDE)

    def show(self):
        if self.status == Card.STATUS_BACKSIDE:
            self.status = Card.STATUS_FRONTSIDE

    def hide(self):
        if self.status == Card.STATUS_FRONTSIDE:
            self.status = Card.STATUS_BACKSIDE

    def visible(self):
        return self.status in (Card.STATUS_FRONTSIDE, Card.STATUS_BACKSIDE)

    def shown(self):
        return self.status == Card.STATUS_FRONTSIDE

