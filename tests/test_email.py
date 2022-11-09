from django.core import mail
from django.urls import reverse

from Main.models import Review
from Users.models import User
from tests.testing_base import BaseCase


class TestEmail(BaseCase):
    test_review = False
    test_review_student = "student-affiliated"
    test_review_reviewer = "reviewer-affiliated"

    test_users = {
        "reviewer-affiliated": (True, False),
        "student-affiliated": (False, False),
        "reviewer-not": (True, False),
        "student-not": (False, False),
    }

    def test_created(self) -> None:
        self.post(
            "student-affiliated",
            reverse("review-create"),
            {"schoology_id": "12.34.56", "rubric": self.rubric.id},
        )
        self.assertEqual(len(mail.outbox), 2)
        for msg in mail.outbox:
            self.assertTrue(
                msg.to[0] == self.users["reviewer-affiliated"].email
                or msg.to[0] == self.users["reviewer-not"].email,
                msg=f"{msg.to[0]} is not a reviewer",
            )
            self.assertEqual(msg.subject, "AM | Review created by student-affiliated")

    def test_claimed(self) -> None:
        self.make_test_review()
        self.post_test_review("reviewer-affiliated", "review-claim")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.users["super"].email)
        self.assertEqual(
            mail.outbox[0].subject, "AM | Review accepted by reviewer-affiliated"
        )

    def test_completed(self) -> None:
        self.make_test_review()
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review(
            "reviewer-affiliated",
            "review-grade",
            {"scores": "[10,2]", "additional_comments": ""},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.users["super"].email)
        self.assertEqual(
            mail.outbox[0].subject, "AM | Review completed by reviewer-affiliated"
        )

    def test_session_checks(self) -> None:
        self.set_user_session("student-affiliated", User.Session.PM)
        self.post(
            "student-affiliated",
            reverse("review-create"),
            {"schoology_id": "12.34.56", "rubric": self.rubric.id},
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_not_self(self) -> None:
        self.set_user_session("reviewer-not", User.Session.PM)
        self.post(
            "reviewer-not",
            reverse("review-create"),
            {"schoology_id": "12.34.56", "rubric": self.rubric.id},
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_no_notification(self) -> None:
        self.users["reviewer-affiliated"].receive_notifications = False
        self.users["reviewer-affiliated"].save()
        self.users["reviewer-not"].receive_notifications = False
        self.users["reviewer-not"].save()
        self.post(
            "student-affiliated",
            reverse("review-create"),
            {"schoology_id": "12.34.56", "rubric": self.rubric.id},
        )
        self.assertEqual(0, len(mail.outbox))
