from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.views.generic import View
from django.urls import reverse
from django.views.decorators.http import last_modified
from django.utils.decorators import classonlymethod
from .models import Game, Player, Card,Image
from gogoedu.models import KanjiLesson, KanjiLevel, Word, myUser,Lesson,Catagory,Kanji
import random 
def get_player(request):
    """
    get the player object of the player making the request.
    the player is identified by a cookie
    """
    player_id = request.COOKIES.get('player_id', '')
    try:
        return Player.objects.get(secretid=player_id)
    except Player.DoesNotExist:
        return None

class GameViewJSON(View):
    @classonlymethod
    def as_conditional_view(cls, *args, **kwargs):
        def last_modified_func(request, urlid):
            game = get_object_or_404(Game, urlid=urlid)
            return game.last_modified
        return last_modified(last_modified_func)(cls.as_view(*args, **kwargs))

    def get(self, request, urlid):
        game = get_object_or_404(Game, urlid=urlid)
        player = get_player(request)
        response = {
            'status': game.get_status_display(),
            'players': {'player%d' % p.id:
                {'name': p.name,
                 'score': p.score,
                 'is_current_player': p.is_current_player()}
                for p in game.players.all()},
            'message': game.message(),
            'cards': {'card%d' % c.id:{
                 'visible': c.visible(),
                 'bgpos': ((c.word )
                           if c.status == Card.STATUS_FRONTSIDE else '<svg width="70" height="70" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0)"><path d="M60.1845 47.6985C56.1346 41.3807 49.2373 37.6083 41.7336 37.6083C34.23 37.6083 27.3326 41.3807 23.2835 47.6985L13.5249 62.9221C11.9057 65.4476 11.1587 68.3659 11.364 71.359C11.5693 74.3527 12.7084 77.1405 14.6578 79.4229C16.6086 81.7033 19.1862 83.262 22.112 83.9308C25.0378 84.5995 28.0371 84.3139 30.7851 83.1061L30.9691 83.0244C37.8836 80.0457 45.7848 80.0732 52.6815 83.1061C54.4606 83.8882 56.3454 84.2837 58.2475 84.2837C59.2815 84.2837 60.3218 84.1663 61.3525 83.9314C64.2783 83.2633 66.8559 81.7046 68.8074 79.4236C70.7574 77.1433 71.8973 74.3548 72.1033 71.3603C72.3093 68.3659 71.5622 65.4483 69.9431 62.9215L60.1845 47.6985Z" fill="white"/><path d="M16.1533 47.6787C19.0565 46.5635 21.262 44.2241 22.3634 41.091C23.4119 38.1096 23.326 34.7436 22.121 31.6125C20.9152 28.4835 18.7221 25.9291 15.9453 24.4192C13.0284 22.8337 9.82385 22.5756 6.92552 23.6927C1.09453 25.9346 -1.58133 33.1403 0.961316 39.7589C2.99241 45.0268 7.72958 48.3523 12.5189 48.3523C13.7418 48.3523 14.9682 48.1353 16.1533 47.6787Z" fill="white"/><path d="M35.0883 35.7516C42.3777 35.7516 48.3083 28.995 48.3083 20.69C48.3083 12.383 42.3777 5.625 35.0883 5.625C27.7995 5.625 21.8697 12.383 21.8697 20.69C21.8697 28.995 27.7995 35.7516 35.0883 35.7516Z" fill="white"/><path d="M57.9192 39.4519H57.9199C59.0412 39.8241 60.1852 40.0019 61.3243 40.0019C66.6403 40.0019 71.821 36.1327 73.7979 30.1863C74.9364 26.7634 74.8615 23.1441 73.5871 19.9958C72.2536 16.6999 69.7824 14.3076 66.6279 13.2591C63.4728 12.2106 60.0609 12.648 57.0197 14.4896C54.1145 16.2488 51.8884 19.1032 50.7513 22.5261C48.3515 29.7469 51.5671 37.3398 57.9192 39.4519V39.4519Z" fill="white"/><path d="M85.7592 37.6941L85.7572 37.692C80.7302 33.9786 73.2122 35.5881 68.9969 41.2818C64.7857 46.9782 65.4442 54.6364 70.4635 58.3525C72.2941 59.7086 74.4571 60.3568 76.6708 60.3568C80.5291 60.3568 84.5432 58.3875 87.2266 54.7662C91.4371 49.0698 90.7793 41.4116 85.7592 37.6941V37.6941Z" fill="white"/></g><defs><clipPath id="clip0"><rect width="90" height="90" fill="white"/></clipPath></defs></svg>')}
                for c in game.cards.all()}
        }
        player = get_player(request)
        if player and player.game == game:
            response['player'] = {
                'name': player.name,
                'can_act': player.can_act(),
                'should_refresh': player.should_refresh()}
        
        return JsonResponse(response)

class GameView(View):
    def get(self, request, urlid):
        accept = request.META.get('HTTP_ACCEPT')
        if 'json' in accept:
            return HttpResponseRedirect(reverse('memory:game_json', args=(urlid,)))
        return self.get_html(request, urlid)

    def get_html(self, request, urlid):
        game = get_object_or_404(Game, urlid=urlid)

        player = get_player(request)

        if game.status == Game.STATUS_WAIT_FOR_PLAYERS:
            if player and player.game == game:
                pass
            else:
                return render(request, 'memory/join.html', {
                    'game': game, 'player':player})

        response = render(request, 'memory/game.html', {
            'game': game, 'player':player})
        # response.setdefault('refresh', '2')
        return response

    def post(self, request, urlid):
        game = get_object_or_404(Game, urlid=urlid)

        player_id = request.COOKIES.get('player_id', '')
        try:
            player = Player.objects.get(secretid=player_id)
        except Player.DoesNotExist:
            player = None

        if game.status == Game.STATUS_WAIT_FOR_PLAYERS:
            if player and player.game == game:
                return HttpResponseRedirect(game.get_absolute_url())

            name = request.POST.get("name", "")

            if not name:
                return render(request, 'memory/join.html', {'error': 'please enter a name', 'game':game})

            player = Player(name=name)

            player = Player(game=game, name=name)
            player.save()

            game.new_game()
            game.save()

            assert game.players.count() == 2, 'expected exactly two players'

            response = HttpResponseRedirect(game.get_absolute_url())
            response.set_cookie('player_id', player.secretid, path=game.get_absolute_url())
            return response

        elif game.status == Game.STATUS_GAME_ENDED:
            game.new_game()
            game.save()

        elif game.current_player == player:
            card_id = request.POST.get("card", "")
            if card_id.isdigit():
                try:
                    card = game.cards.get(id=card_id)
                except Card.DoesNotExist:
                    pass
                else:
                    game.show_card(card)
            
        accept = request.META.get('HTTP_ACCEPT')
        if 'json' in accept:
            return HttpResponseRedirect(reverse('memory:game_json', args=(urlid,)))
        return HttpResponseRedirect(game.get_absolute_url())


class Welcome(View):
    def post(self, request):
        '''create a new game and redict to it'''
        name = request.POST.get("name", "")
        lessonid = request.POST.get("lesson", "")
        kanjilessonid = request.POST.get("kanjilesson", "")
        if not name:
            return render(request, 'memory/newgame.html', {'error': 'please enter a name'})
        if not lessonid:
            if kanjilessonid:
                game = Game()
                game.save()
                player = Player(game=game, name=name)
                player.save()
                kanjilesson = get_object_or_404(KanjiLesson, id = kanjilessonid)
                word_list = kanjilesson.kanji_set.all()
                images = Image.objects.all()
                print("zo kanji")
                id_list = word_list.values_list('id', flat=True)
                
                random_profiles_id_list = random.sample(list(id_list), min(len(id_list), images.count()))
                x=images.count()
                for image in images:
                    x=x-1
                    image.kanji=Kanji.objects.get(id=random_profiles_id_list[x])
                    image.status=2
                    image.save()
                
                

                response = HttpResponseRedirect(game.get_absolute_url())
                response.set_cookie('player_id', player.secretid, path=game.get_absolute_url())
            else:
                return render(request, 'memory/newgame.html', {'error': 'please enter a lesson'})
        else:
            print("zo tu vung")
            game = Game()
            game.save()
            player = Player(game=game, name=name)
            player.save()
            lesson = get_object_or_404(Lesson, id = lessonid)
            word_list = lesson.word_set.all()
            images = Image.objects.all()
            
            id_list = word_list.values_list('id', flat=True)
            
            random_profiles_id_list = random.sample(list(id_list), min(len(id_list), images.count()))
            x=images.count()
            for image in images:
                x=x-1
                image.word=Word.objects.get(id=random_profiles_id_list[x])
                image.status=1
                image.save()
            
            

            response = HttpResponseRedirect(game.get_absolute_url())
            response.set_cookie('player_id', player.secretid, path=game.get_absolute_url())
        return response

    def get(self, request):
        category = Catagory.objects.all()
        kanjilevel= KanjiLevel.objects.all()
        context={
            'category':category,
            'kanjilevel':kanjilevel,
        }
        return render(request, 'memory/newgame.html',context)
