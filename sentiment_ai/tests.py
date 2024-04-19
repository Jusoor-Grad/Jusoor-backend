from django.test import TestCase, tag
from sentiment_ai.views import SentimentReportViewset
from rest_framework.test import APIRequestFactory
# Create your tests here.

@tag('sntmnt-report')
class SentimentReportTest(TestCase):
    
    def setUp(self) -> None:
        viewset = SentimentReportViewset
        self.list = viewset.as_view({'get': 'list'})
        self.retrieve = viewset.as_view({'get': 'retrieve'})


@tag('sntmnt-msg')
class MessageSentimentTest(TestCase):
    """
        class to test the sentiment of a message
    """
    
    def setUp(self) -> None:
        pass


class SentimentUtilsTest(TestCase):
    """
        class to test all the sentiment-related utilities used in the functoinality
        of claculating sentiment
    """
    pass

