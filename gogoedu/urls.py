from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('register/', views.register, name='register'),
	path('profile/<int:pk>', views.Profile.as_view(), name='profile-detail'),
	path('lesson/<int:pk>', views.Lesson_detail.as_view(), name='lesson-detail'),
	path('lesson/<int:pk>/tests/', views.GetTestInfo.as_view(), name='lesson-tests'),
	path('lesson/<int:pk>/words/<int:wordid>/learned/', views.MarkLearned.as_view(), name='mark-learned'),
	path('catagory/', views.CatagoryListView.as_view(), name='catagory'),
	path('catagory/<int:pk>', views.CatagoryDetailView.as_view(), name='lesson'),
	path('grammar/', views.GrammarLevelListView.as_view(), name='grammar'),
	path('grammar/<int:pk>', views.GrammarLevelDetailView.as_view(), name='grammar-lesson'),
	path('grammar/<int:grammar_lesson_id>/lesson/<int:pk>', views.Grammar_lesson_detail.as_view(), name='grammar-detail'),
	path('kanji/', views.KanjiLevelListView.as_view(), name='kanji'),
	path('kanji/<int:pk>', views.KanjiLevelDetailView.as_view(), name='kanji-lesson'),
	path('kanji/<int:kanji_lesson_id>/lesson/<int:pk>', views.Kanji_lesson_detail.as_view(), name='kanji-detail'),
	path('lesson/<int:pk>/kanjis/<int:wordid>/learned/', views.MarkLearnedKanji.as_view(), name='mark-learned-kanji'),
	path('reading/', views.ReadingLevelListView.as_view(), name='reading'),
	path('reading/<int:pk>', views.ReadingLevelDetailView.as_view(), name='reading-lesson'),
	path('reading/<int:reading_lesson_id>/lesson/<int:pk>', views.Reading_lesson_detail.as_view(), name='reading-detail'),
	path('listening/', views.ListeningLevelListView.as_view(), name='listening'),
	path('listening/<int:pk>', views.ListeningLevelDetailView.as_view(), name='listening-lesson'),
	path('listening/<int:listening_lesson_id>/lesson/<int:pk>', views.Listening_lesson_detail.as_view(), name='listening-detail'),
	path('profile/<int:pk>/edit', views.profile_update, name='profile-update'),
	path('test/<int:pk>', views.test_detail_view, name='test-detail'),
	path('test/<int:pk>/paused', views.TestPause.as_view(), name='test-paused'),
	path('test/<int:pk>/saved', views.TestSave.as_view(), name='test-saved'),
	path('results/<int:pk>', views.show_form_correct, name='show_results'),
	path('reading/results/<int:pk>', views.show_form_correct_reading, name='show_results_reading'),
	path('listening/results/<int:pk>', views.show_form_correct_listening, name='show_results_listening'),
	path('activate/<uidb64>/<token>', views.activate, name='activate'),
	path('register/<int:pk>/activation', views.activation_request, name='account-activation'),
	path('summary/', views.summary_detail_view, name='show_summary'),
	path('summary/chart/', views.ChartData.as_view()),
	path('flashcard/', views.flashcard_view, name='flashcard'),
	path('leaderboard/', views.leaderboard_view, name='leaderboard'),
	path('privacy/', views.privacy_view, name='privacy'),
	path('flashcard/<int:pk>', views.view_card_set, name = 'view_card_set'), 
	path('flashcard/<int:pk>/test', views.flashcard_test, name = 'flashcard_test'), 
	path('badge', views.BadgeView.as_view(), name='badge'),
    path('badge/award-badge/<int:badge_id>/', views.AwardBadgeView.as_view(), name='award-badge'),
    path('badge/revoke-badge/<int:badge_id>/', views.RevokeBadgeView.as_view(), name='revoke-badge'),
	path('profile/<int:pk>/<int:badge_id>/', views.SetBadgeView.as_view(), name='set-badge'),
	path('alphabet', views.alphabet, name='alphabet'),
	path('mission/', views.MissionView.as_view()),
	path('alphabet/getfinish', views.CheckAlphabet.as_view()),
]
