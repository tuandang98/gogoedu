from django.conf.urls import url

from . import views

app_name = 'memory'
urlpatterns = [
    url(r'^$', views.Welcome.as_view(), name='welcome'),
    url(r'^(?P<urlid>[0-9a-z]+)/$', views.GameView.as_view(), name='game'),
    url(r'^(?P<urlid>[0-9a-z]+)/json$', views.GameViewJSON.as_conditional_view(), name='game_json'),
]
