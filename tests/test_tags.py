from django.contrib import messages
from django.test import TestCase

from Main.models import Review
from Main.templatetags import common_tags, review_tags
from tests.test_review import BaseCase


class CommonTagsTest(TestCase):

    def test_make_spaces(self) -> None:
        self.assertEqual(common_tags.make_spaces("test-value"), "test value")
        self.assertEqual(common_tags.make_spaces("test_value"), "test value")

    def test_get_link_class(self) -> None:
        self.assertEqual(common_tags.get_link_class("edit"), "link-primary")
        self.assertEqual(common_tags.get_link_class("delete"), "link-danger")

    def test_get_alert_class(self) -> None:
        self.assertEqual(common_tags.get_alert_class(messages.SUCCESS), 'alert-success')
        self.assertEqual(common_tags.get_alert_class(messages.INFO), 'alert-info')
        self.assertEqual(common_tags.get_alert_class(messages.ERROR), 'alert-danger')
        self.assertEqual(common_tags.get_alert_class(messages.WARNING), 'alert-warning')

    def test_get_icon_class(self) -> None:
        self.assertEqual(common_tags.get_icon_class(messages.SUCCESS), 'bi bi-check-circle')
        self.assertEqual(common_tags.get_icon_class(messages.INFO), 'bi bi-info-circle')
        self.assertEqual(common_tags.get_icon_class(messages.ERROR), 'bi bi-exclamation-circle')
        self.assertEqual(common_tags.get_icon_class(messages.WARNING), 'bi bi-exclamation-triangle')


class TestReviewTags(BaseCase):

    def test_session(self):
        self.assertIn(self.review, review_tags.get_session(Review.objects.all(), "AM"))
        self.assertNotIn(self.review, review_tags.get_session(Review.objects.all(), "PM"))
