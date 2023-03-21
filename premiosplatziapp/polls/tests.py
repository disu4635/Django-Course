import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

#Models
#Views
class QuestionModelTest(TestCase):
    
    def test_was_published_recently_with_future_questions(self):
        """was_published_recently returns False for questions wose pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text ='¿Quién es el mejor Course Director de Platzi', pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_current_questions(self):
        """was_published_recently returns True for questions whose pub_date is now"""
        time = timezone.now()
        future_question = Question(question_text ='¿Quién es el mejor Course Director de Platzi', pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)
    
    def test_was_published_recently_with_past_questions(self):
        """was_published_recently returns True for questions whose pub_date is betwen now and 1 day ago"""
        time = timezone.now() - datetime.timedelta(days=0.5)
        future_question = Question(question_text ='¿Quién es el mejor Course Director de Platzi', pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Create a question with the given "question_text", and published the given
    number of days offset to now(negative for question in the past, positive for
    questions that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text = question_text, pub_date=time)

class QuestionIndexViewTest(TestCase):

    def test_no_questions(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        #Make a request type get to the url ,this url is given by reverse
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are aviable")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
    
    def test_no_future_questions(self):
        """If a question is in the future, it doesn't be in the page"""
        create_question("Future question", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are aviable")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
    
    def test_past_questions(self):
        """A past question must be in the page"""
        question = create_question("Past question", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """Eve if both past and future question exist, only past questions are displayed."""
        past_question = create_question(question_text="Past question", days=-30)
        future_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        past_question1 = create_question(question_text="Past question 1", days=-30)
        past_question2 = create_question(question_text="Past question 2", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1, past_question2]
        )
    
    def test_two_future_questions(self):
        """The questions index page may not display questions."""
        future_question1 = create_question(question_text="Future question 1", days=30)
        future_question2 = create_question(question_text="Future question 2", days=40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],[]
        )

class QuestionDetailViewTest(TestCase):
    
    def test_future_Question(self):
        """The detail view of a question with a pub_date in the future returns a 404 error not found
        """
        future_question = create_question(question_text="Future question", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_Question(self):
        """The detail view of a question with a pub_date in the past displays the question's"""
        past_question = create_question(question_text="Past question", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
    
class QuestionResultViewTest(TestCase):

    def test_no_future_questions(self):
        """The result view should return a 404 error with questions published in the future"""
        future_question = create_question(question_text="Future question", days=30)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_Question(self):
        """The result view should return a 200 status code with questions published in the past"""
        past_question = create_question(question_text="Past question", days=-30)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

        