from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from gogoedu.models import myUser, Lesson, Word, Catagory, Test, UserTest, Question, Choice, UserAnswer, UserWord,TestResult
class CatagoryListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_catagories = 10

        for catagory_id in range(number_of_catagories):
            Catagory.objects.create(
                name=f' Le Minh Quang {catagory_id}',
            )
           
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/gogoedu/catagory/')
        self.assertEqual(response.status_code, 200)
           
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('catagory'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('catagory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gogoedu/catagory_list.html')
        
    def test_pagination_is_two(self):
        response = self.client.get(reverse('catagory'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['catagory_list']) == 2)

    def test_lists_all_catagories(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('catagory')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['catagory_list']) == 2)

class ProfileUpdateViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = myUser.objects.create_user(username='testuser1', password='2HJ1vRV0Z&3iD', is_active=True)
        test_user2 = myUser.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', is_active=True)

        test_user1.save()
        test_user2.save()

        self.test_user1 = test_user1
        self.test_user2 = test_user2

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile-update', kwargs={'pk': self.test_user2.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('profile-update', kwargs={'pk': self.test_user2.pk}))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('profile-update', kwargs={'pk': self.test_user2.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'gogoedu/myuser_update.html')

    def test_redirects_to_profile_update_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        first_name, last_name, email = 'Nguyen', 'Quang Anh', 'test11@gmail.com'
        response = self.client.post(reverse('profile-update', kwargs={'pk': self.test_user2.pk}),
                                    {'first_name': first_name,
                                     'last_name': last_name,
                                     'email': email})
        self.assertEqual(response.status_code, 200)

    def test_invalid_user_redirect(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('profile-update', kwargs={'pk': self.test_user1.pk}))
        self.assertTrue(response.url.startswith('/gogoedu/'))


class Test_form_correct(TestCase):
    def setUp(self):
        test_user1 = myUser.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = myUser.objects.create_user(
            username='testuser2', password='1X<ISRUkw+tuK')
        test_user2.save()
        # Create a test
        self.test_user1 = test_user1
        self.test_user2 = test_user2
        test = Test.objects.create(name='Love Shiba', time=20, question_num=20)
        test.save()
        self.test = test
        question = test.question_set.create(question_text='Do u know Shiba?')
        question.save()

        choice1 = question.choice_set.create(choice_text='Cat?')
        choice2 = question.choice_set.create(choice_text='Dog?', correct=True)
        choice3 = question.choice_set.create(choice_text='Dolphin?')
        choice4 = question.choice_set.create(choice_text='Hito?')
        choice1.save()
        choice2.save()
        choice3.save()
        choice4.save()

        user1_answer = test_user1.useranswer_set.create(
            question=question, choice=choice2)
        user1_answer.save()
        user2_answer = test_user2.useranswer_set.create(
            question=question, choice=choice3)
        user2_answer.save()
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('show_results', kwargs={'pk': self.test.id}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('show_results', kwargs={'pk': self.test.id}))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'gogoedu/show_results.html')


    def test_answer_correct(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('show_results', kwargs={'pk': self.test.id}))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(str(response.context['score']), '1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'gogoedu/show_results.html')


    def test_result_incorrect(self):
        login = self.client.login(username='testuser2', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('show_results', kwargs={'pk': self.test.id}))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(str(response.context['score']), '0')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'gogoedu/show_results.html')
        
        
    def test_save_result(self):
        login = self.client.login(username='testuser2', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('show_results', kwargs={'pk': self.test.id}))
        result = TestResult.objects.filter(user=self.test_user2)
        self.assertTrue(result.count())
