from django.test import TestCase, Client
from django.urls import reverse
from user.models import User
from core.models import Task
from topic.models import Topic
from judgment.models import Judgment

class TestViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create(
            username='testuser', 
            email='test@test.com', 
            password='testpassword'
        )

        self.topic = Topic.objects.create(
            uuid='testuuid', 
            title='should we test our code?'
        )



    def test_home_GET(self):
        self.client = Client()
        
        # Login!
        response = self.client.get(reverse('core:home'))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/accounts/login/?next=/')

        # After login!
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')


    def test_home_POST(self):
        self.client.force_login(self.user)
        task = Task.objects.create(
                user=self.user,
                topic=self.topic,
        )

        response = self.client.post(reverse('core:home'), {
            "selected_question": task.id})
        self.assertEquals(response.status_code, 302)
        
        judgment = Judgment.objects.get(id=response.url.split("/")[-2])
        self.assertEquals(judgment.task.id, task.id)
        self.assertEquals(judgment.user.id, self.user.id)


    def test_single_round_results_GET(self):
        self.client.force_login(self.user)
        task = Task.objects.create(
                user=self.user,
                topic=self.topic,
        )

        judgment = Judgment.objects.create(
                user=self.user,
                task=task,
                is_round_done=True,
                best_answers='testdoc1--testdoc2--testdoc3'
        )

        response = self.client.get(reverse('core:single_round_results', args=[self.user.id, judgment.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'single_round_results.html')
        self.assertEquals(response.context['question_content'], self.topic.title)


    def test_single_round_results_POST(self):
        self.client.force_login(self.user)
        task = Task.objects.create(
                user=self.user,
                topic=self.topic,
                best_answers='testdoc1--testdoc2--testdoc3--'
        )

        judgment = Judgment.objects.create(
                user=self.user,
                task=task,
                is_round_done=True,
                before_state="testbeforestate".encode('ascii'),
                after_state="testafterstate".encode('ascii'),
                best_answers='testdoc1--testdoc2--testdoc3'
        )
        self.user.latest_judgment = judgment
        self.user.save()

        response = self.client.post(reverse('core:single_round_results', args=[self.user.id, judgment.id]), {
            "no": "no"
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse('core:home'))

        response = self.client.post(reverse('core:single_round_results', args=[self.user.id, judgment.id]), {
            "prev": "prev"
        })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse('judgment:judgment', args=[self.user.id, judgment.id]))

        response = self.client.post(reverse('core:single_round_results', args=[self.user.id, judgment.id]), {
            "yes": "yes"
        })
        self.assertEquals(response.status_code, 302)
        new_judgment = Judgment.objects.get(id=int(response.url.split("/")[-2]))
        self.assertEquals(new_judgment.task.id, task.id)
        self.assertEquals(new_judgment.user.id, self.user.id)


    def test_task_results_GET(self):
        self.client.force_login(self.user)
        task = Task.objects.create(
                user=self.user,
                topic=self.topic,
                best_answers='testdoc1--testdoc2--testdoc3--'
        )

        response = self.client.get(reverse('core:task_results', args=[self.user.id, task.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_results.html')
        self.assertEquals(response.context['question_content'], self.topic.title)

