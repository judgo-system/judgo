import pickle
from django.test import TestCase, Client
from django.urls import reverse
from user.models import User
from core.models import Task
from topic.models import Topic
from document.models import Document
from judgment.models import Judgment
from interfaces.pref import pref

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

        self.task = Task.objects.create(
                user=self.user,
                topic=self.topic,
        )


        for doc in ["A", "B", "C","D", "E"]:
            d = Document.objects.create(uuid=doc)
            d.topics.add(self.topic)
            
        self.pref = pref(["A", "B", "C","D", "E"], 3)

        self.parent = Judgment.objects.create(
                user=self.user, 
                task=self.task,
                after_state=pickle.dumps(self.pref)
        )
        self.judgment = Judgment.objects.create(
                user=self.user,
                task=self.task,
                parent=self.parent,
                before_state=pickle.dumps(self.pref)
        )

        self.user.latest_judgment = self.judgment
        self.user.save()


        
    def test_judgment_GET(self):
        self.client.force_login(self.user)
           
        judgment = Judgment.objects.create(
                user=self.user,
                task=self.task,
                before_state=pickle.dumps(self.pref)
        )
        
        response = self.client.get(reverse('judgment:judgment', args=(self.user.id, judgment.id)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'judgment.html')



    def test_judgment_POST(self):
        self.client.force_login(self.user)


        # Test POST with "prev" keyword
        response = self.client.post(reverse('judgment:judgment', args=(self.user.id, self.judgment.id)), {
            "prev": "yes"})
        self.assertEquals(response.status_code, 302)
        self.assertEqual(response.url, reverse('judgment:judgment', args=(self.user.id, self.parent.id)))

        # Test POST with "left" keyword
        self.user.latest_judgment = self.judgment
        self.user.save()
        response = self.client.post(reverse('judgment:judgment', args=(self.user.id, self.judgment.id)), {
            "left": "yes"})
        self.assertEquals(response.status_code, 302)
        state = pickle.loads(Judgment.objects.get(id=response.url.split("/")[-2]).before_state)
        self.assertEqual(str(state), "(('E ('D)) ('C) ('B) ('A)) []")


        # Test POST with "right" keyword
        self.user.latest_judgment = self.judgment
        self.user.save()
        response = self.client.post(reverse('judgment:judgment', args=(self.user.id, self.judgment.id)), {
            "right": "yes"})
        self.assertEquals(response.status_code, 302)
        state = pickle.loads(Judgment.objects.get(id=response.url.split("/")[-2]).before_state)
        self.assertEqual(str(state), "(('D ('E)) ('C) ('B) ('A)) []")

        # Test POST with "equal" keyword
        self.user.latest_judgment = self.judgment
        self.user.save()
        response = self.client.post(reverse('judgment:judgment', args=(self.user.id, self.judgment.id)), {
            "equal": "yes"})
        self.assertEquals(response.status_code, 302)
        state = pickle.loads(Judgment.objects.get(id=response.url.split("/")[-2]).before_state)
        self.assertEqual(str(state), "(('E) ('C) ('B) ('A)) [('E', 'D')]")
