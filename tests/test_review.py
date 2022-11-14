from json import JSONDecoder, JSONEncoder

from django.core import mail
from django.urls import reverse

from Instructor.models import ScoredRow, Rubric
from Main.forms import GradeReviewForm, ReviewForm
from Main.models import Review
from Users.models import User
from tests.testing_base import BaseCase as OldBaseCase, SimpleBaseCase


class BaseCase(OldBaseCase):
    test_users = {
        "reviewer-affiliated": (True, False),
        "student-affiliated": (False, False),
        "reviewer-not": (True, False),
        "student-not": (False, False),
    }

    test_review_student = "student-affiliated"
    test_review_reviewer = "reviewer-affiliated"


class ReviewAccessTest(BaseCase):
    # noinspection SpellCheckingInspection
    expected = {
        "create": ("--yyy",),
        "edit": ("-ynnn", "-ynnn"),
        "cancel": ("nynnn", "nynnn", "nnnnn"),
        "delete": ("nnnny", "nnnny", "nnnny"),
        "claim": ("-nynn", "nnnnn", "nnnnn"),
        "abandon": ("nnnnn", "ynnnn", "nnnnn"),
        "grade": ("nnnnn", "ynnnn", "nnnnn"),
        "view": ("-ynny", "yynny", "yynny"),
    }

    def setUp(self) -> None:
        super(ReviewAccessTest, self).setUp()
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review(
            "reviewer-affiliated",
            "review-grade",
            {"scores": "[10,2]", "additional_comments": ""},
        )
        self.set_test_review_status(Review.Status.OPEN)

    def assertResponses(self, expected_key, add_pk=True, http_type="get") -> None:
        target_statuses = self.expected[expected_key]
        if add_pk:
            url = reverse(f"review-{expected_key}", kwargs={"pk": self.review.id})
        else:
            url = reverse(f"review-{expected_key}")
        for index in range(len(target_statuses)):
            target_responses = target_statuses[index]
            self.set_test_review_status(Review.Status.values[index])
            for code_index, expected in enumerate(target_responses):
                if expected != "-":
                    if http_type == "get":
                        response = self.get(list(self.clients.keys())[code_index], url)
                    else:
                        response = self.post(list(self.clients.keys())[code_index], url)

                    if expected == "y":
                        self.assertIn(response.status_code, (200, 302))
                    elif expected == "n":
                        if http_type == "get":
                            self.assertIn(
                                response.template_name[0],
                                ["errors/403.html", "errors/404.html"],
                            )
                        else:
                            self.assertIn(
                                response.templates[0].name,
                                ("errors/404.html", "errors/403.html"),
                            )
                    else:
                        self.fail("Invalid Setup Of Expected")

    def test_create(self) -> None:
        self.assertResponses("create", add_pk=False)

    def test_edit(self) -> None:
        self.assertResponses("edit")

    def test_cancel(self) -> None:
        self.assertResponses("cancel")

    def test_delete(self) -> None:
        self.assertResponses("delete")

    def test_claim(self) -> None:
        self.assertResponses("claim", http_type="post")

    def test_abandon(self) -> None:
        self.assertResponses("abandon")

    def test_grade(self) -> None:
        self.assertResponses("grade")

    def test_view(self) -> None:
        self.assertResponses("view")


class HomeListTest(BaseCase):
    expected = {
        "O": ("-", "active", "open", "none"),
        "A": ("assigned", "active", "none", "none"),
        "C": ("completed", "completed", "none", "none"),
    }

    url = reverse("home")

    def assertStatus(self, status_code):
        self.set_test_review_status(status_code)
        for index, group in enumerate(self.expected[status_code]):
            if group != "-":
                response = self.get(list(self.clients.keys())[index], self.url)
                if group == "none":
                    for not_group in ["open", "assigned", "completed", "active"]:
                        self.assertNotIn(
                            self.review, response.context.get(not_group, [])
                        )
                else:
                    self.assertIn(self.review, response.context.get(group, []))

    def test_open(self) -> None:
        self.assertStatus("O")

    def test_open_different_session(self) -> None:
        self.set_user_session("reviewer-not", User.Session.PM)
        response = self.get("reviewer-not", self.url)
        self.assertNotIn(self.review, response.context.get("open", []))

    def test_assigned(self) -> None:
        self.assertStatus("A")

    def test_closed(self) -> None:
        self.assertStatus("C")


class CompleteListTest(BaseCase):
    def setUp(self) -> None:
        super(CompleteListTest, self).setUp()
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review(
            "reviewer-affiliated",
            "review-grade",
            {"scores": "[10,2]", "is_draft": "false"},
        )

    def assertInContext(self, user, params=""):
        response = self.get(user, reverse("review-complete") + params)
        self.assertIn(self.review, response.context.get("reviews", []))

    def assertNotInContext(self, user, params=""):
        response = self.get(user, reverse("review-complete") + params)
        self.assertNotIn(self.review, response.context.get("reviews", []))

    def test_access(self):
        self.assertInContext("student-affiliated")
        self.assertInContext("reviewer-affiliated")
        self.assertNotInContext("student-not")
        self.assertNotInContext("reviewer-not")

    def test_pagination(self):
        response = self.get("student-affiliated", reverse("review-complete"))
        self.assertFalse(response.context["page_obj"].has_other_pages())
        for i in range(0, 12):
            new_review = self.make_arb_review(
                "student-affiliated",
                "reviewer-affiliated",
                Review.Status.ASSIGNED,
                "12.34.56",
            )
            self.post_review(
                "reviewer-affiliated",
                "review-grade",
                new_review.id,
                {"scores": "[10,2]", "is_draft": "false"},
            )
        response = self.get("student-affiliated", reverse("review-complete"))
        self.assertTrue(response.context["page_obj"].has_other_pages())
        response = self.get(
            "student-affiliated", reverse("review-complete") + "?page=2"
        )
        self.assertEqual(response.status_code, 200)

    def test_instructor_view(self):
        self.assertInContext("super", params="?session=AM")
        self.assertNotInContext("super", params="?session=PM")

    def test_bad_session(self):
        response = self.get("super", reverse("review-complete"), {"session": "BAD"})
        self.assertIn("errors/404.html", response.template_name)


class BaseReviewAction(OldBaseCase):
    test_users = OldBaseCase.USER_STUDENT_REVIEWER
    start_status = Review.Status.OPEN

    def setUp(self) -> None:
        super(BaseReviewAction, self).setUp()
        if self.test_review:
            self.set_test_review_status(self.start_status)
            self.refresh_test_review()


class ReviewCreateTest(BaseReviewAction):
    test_review = False

    def test_create(self) -> None:
        self.post(
            "student",
            reverse("review-create"),
            {"schoology_id": "12.34.56", "rubric": str(self.rubric.id)},
        )
        try:
            self.review = Review.objects.get(schoology_id="12.34.56")
        except Review.DoesNotExist:
            self.fail("Review Not Created Successfully")

    def test_limit(self) -> None:
        url = reverse("review-create")
        for x in range(4):
            self.post(
                "student",
                url,
                {"schoology_id": "12.34.56", "rubric": str(self.rubric.id)},
            )
        self.assertEqual(
            Review.objects.filter(
                student=self.users["student"], status=Review.Status.OPEN
            ).count(),
            2,
        )


class ReviewSchoologyIDValidationTest(OldBaseCase):
    test_users = SimpleBaseCase.USER_SINGLE_STUDENT
    test_review = False

    def assertBad(self, test_id):
        form = ReviewForm(
            {"schoology_id": test_id, "rubric": str(self.rubric.id)},
            user=self.users["test-user"],
        )
        self.assertFalse(form.is_valid())

    def test_too_short(self):
        self.assertBad("12")

    def test_too_long(self):
        self.assertBad("1234567890")

    def test_no_dots(self):
        self.assertBad("123456")

    def test_not_dots(self):
        self.assertBad("12/34/56")

    def test_not_number(self):
        self.assertBad("as.34.56")

    def test_negative(self):
        self.assertBad("-5.45.12")


class ReviewCancelUnclaimedTest(BaseReviewAction):
    test_review = True

    test_review_student = "student"
    test_review_reviewer = None

    def test_cancel(self) -> None:
        self.post_test_review("student", "review-cancel")
        self.assertTrue(Review.objects.filter(id=self.review.id).count() == 0)


class ReviewCancelClaimedTest(ReviewCancelUnclaimedTest):
    start_status = Review.Status.ASSIGNED


class ReviewEditUnclaimedTest(BaseReviewAction):
    test_review = True

    test_review_student = "student"
    test_review_reviewer = None

    def test_edit(self) -> None:
        self.post_test_review(
            "student",
            "review-edit",
            {"schoology_id": "12.34.78", "rubric": self.rubric.id},
        )
        self.assertTrue(Review.objects.filter(schoology_id="12.34.78").count() > 0)


class ReviewEditClaimedTest(ReviewEditUnclaimedTest):
    start_status = Review.Status.ASSIGNED
    test_review_reviewer = "reviewer"


class ReviewClaimTest(BaseReviewAction):
    test_review = True

    test_review_student = "student"
    test_review_reviewer = None

    def test_claim(self) -> None:
        self.post_test_review("reviewer", "review-claim")
        self.refresh_test_review()
        self.assertEqual(Review.Status.ASSIGNED, self.review.status)
        self.assertEqual(self.users["reviewer"], self.review.reviewer)

    def test_claim_different_session(self) -> None:
        self.set_user_session("reviewer", User.Session.PM)
        response = self.post_test_review("reviewer", "review-claim")
        self.assertEqual(response.templates[0].name, "errors/404.html")

    def test_limit(self) -> None:
        self.make_arb_user("student-2", "test-password")
        for x in range(3):
            target_user = "student" if x < 1 else "student-2"
            self.post(
                target_user,
                reverse("review-create"),
                {"schoology_id": f"12.34.0{x}", "rubric": self.rubric.id},
            )
            review = Review.objects.get(schoology_id=f"12.34.0{x}")
            self.post_review("reviewer", "review-claim", review.id)
        self.assertEqual(
            Review.objects.filter(
                reviewer=self.users["reviewer"], status=Review.Status.ASSIGNED
            ).count(),
            2,
        )


class ReviewAbandonTest(BaseReviewAction):
    test_review = True
    test_review_student = "student"
    test_review_reviewer = "reviewer"
    start_status = Review.Status.ASSIGNED

    def test_abandon(self) -> None:
        self.post_test_review("reviewer", "review-abandon")
        self.refresh_test_review()
        self.assertEqual(Review.Status.OPEN, self.review.status)
        self.assertIsNone(self.review.reviewer)


class ReviewGradeTest(BaseReviewAction):
    test_review = True
    test_review_student = "student"
    test_review_reviewer = "reviewer"
    start_status = Review.Status.ASSIGNED

    def assertScoresEqual(self, source_str, target_str):
        self.post_test_review(
            "reviewer",
            "review-grade",
            {"scores": source_str, "additional_comments": "", "is_draft": "false"},
        )
        self.refresh_test_review()
        self.assertEqual(self.review.score_fraction(), target_str)

    def assertBad(self, src_str):
        form = GradeReviewForm(
            {"scores": src_str, "additional_comments": ""}, instance=self.review
        )
        self.assertFalse(form.is_valid())

    def test_draft(self) -> None:
        self.post_test_review(
            "reviewer",
            "review-grade",
            {
                "scores": "[5,2]",
                "additional_comments": "test comment",
                "is_draft": "true",
            },
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        self.assertEqual(self.review.score_fraction(), None)
        self.assertEqual(self.review.additional_comments, "test comment")
        self.assertEqual(self.review.scoredrow_set.all().count(), 2)
        self.assertEqual(self.review.scoredrow_set.get(source_row__index=0).score, 5)
        self.assertEqual(self.review.scoredrow_set.get(source_row__index=1).score, 2)

    def test_draft_empties(self) -> None:
        self.post_test_review(
            "reviewer",
            "review-grade",
            {
                "scores": "[5,-1]",
                "additional_comments": "test comment",
                "is_draft": "true",
            },
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        self.assertEqual(self.review.score_fraction(), None)
        self.assertEqual(self.review.additional_comments, "test comment")
        self.assertEqual(self.review.scoredrow_set.all().count(), 2)
        self.assertEqual(self.review.scoredrow_set.all()[0].score, 5)
        self.assertEqual(self.review.scoredrow_set.all()[1].score, -1)

    def test_draft_and_rubric_change(self) -> None:
        self.post_test_review(
            "reviewer",
            "review-grade",
            {
                "scores": "[5,-1]",
                "additional_comments": "test comment",
                "is_draft": "true",
            },
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        new_rubric = Rubric.objects.create(name="Test Rubric 2", max_score=10)
        new_rubric.save()
        self.post_test_review(
            "student",
            "review-edit",
            {"schoology_id": "12.34.78", "rubric": new_rubric.id},
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        self.assertEqual(self.review.scoredrow_set.all().count(), 0)

    def test_draft_and_rubric_no_change(self) -> None:
        self.post_test_review(
            "reviewer",
            "review-grade",
            {
                "scores": "[5,-1]",
                "additional_comments": "test comment",
                "is_draft": "true",
            },
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        self.post_test_review(
            "student",
            "review-edit",
            {"schoology_id": "12.34.78", "rubric": self.rubric.id},
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        self.assertEqual(self.review.scoredrow_set.all().count(), 2)
        self.assertEqual(self.review.scoredrow_set.all()[0].score, 5)
        self.assertEqual(self.review.scoredrow_set.all()[1].score, -1)

    def test_draft_no_email(self) -> None:
        self.post_test_review(
            "reviewer",
            "review-grade",
            {
                "scores": "[5,-1]",
                "additional_comments": "test comment",
                "is_draft": "true",
            },
        )
        self.refresh_test_review()
        self.assertEqual(self.review.status, Review.Status.ASSIGNED)
        self.assertEqual(len(mail.outbox), 0)

    def test_grade(self) -> None:
        self.assertScoresEqual("[5,2]", "7.0/12.0")
        self.assertEqual(
            User.objects.get(pk=self.users["student"].id).reviews_done_as_reviewee, 1
        )
        self.assertEqual(
            User.objects.get(pk=self.users["student"].id).reviews_done_as_reviewer, 0
        )
        self.assertEqual(
            User.objects.get(pk=self.users["reviewer"].id).reviews_done_as_reviewer, 1
        )
        self.assertEqual(
            User.objects.get(pk=self.users["reviewer"].id).reviews_done_as_reviewee, 0
        )

    def test_grade_not_json(self) -> None:
        self.assertBad("not json")

    def test_grade_non_numeric(self) -> None:
        self.assertBad('["not","numeric"]')

    def test_grade_none(self) -> None:
        self.assertBad("[]")

    def test_grade_too_many(self) -> None:
        self.assertBad("[1,1,1,1,1,1]")

    def test_grade_not_scores(self) -> None:
        self.assertBad("[15, 2]")

    def test_grade_in_range_but_not_valid(self) -> None:
        self.assertBad("[4, 2]")

    def test_grade_zeros(self) -> None:
        self.assertBad("[0, 0]")

    def test_grade_under_limit(self) -> None:
        self.assertBad("[-50,2]")

    def test_no_instance(self) -> None:
        self.assertRaises(ValueError, GradeReviewForm)


class UpdateReviewScoreOnRubricEditTest(BaseCase):
    test_users = BaseCase.USER_STUDENT_REVIEWER

    test_review_student = "student"
    test_review_reviewer = "reviewer"

    def setUp(self) -> None:
        super(UpdateReviewScoreOnRubricEditTest, self).setUp()
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review(
            "reviewer", "review-grade", {"scores": "[10,2]", "is_draft": "false"}
        )

    def test_new_rows(self) -> None:
        new_obj = JSONDecoder().decode(self.get_test_rubric_json())
        new_obj.append(
            {
                "name": "New Row",
                "description": "New Row 3",
                "cells": [
                    {"score": 1, "description": "New Cell 1"},
                    {"score": 0, "description": "New Cell 2"},
                ],
            }
        )
        self.post(
            "super",
            reverse("rubric-edit", kwargs={"pk": self.rubric.id}),
            {"name": "Edited Rubric", "rubric": JSONEncoder().encode(new_obj)},
        )
        self.assertEqual(
            ScoredRow.objects.filter(parent_review__id=self.review.id).count(), 3
        )
        self.assertEqual(
            ScoredRow.objects.get(parent_review=self.review, source_row__index=2).score,
            -1,
        )

    def test_delete_row(self):
        new_obj: list = JSONDecoder().decode(self.get_test_rubric_json())
        new_obj.pop(1)
        self.clients["super"].post(
            reverse("rubric-edit", kwargs={"pk": self.rubric.id}),
            {"name": "Edited Rubric", "rubric": JSONEncoder().encode(new_obj)},
        )
        self.assertEqual(
            ScoredRow.objects.filter(parent_review__id=self.review.id).count(), 1
        )


class LeaderBoardTest(BaseCase):
    test_users = BaseCase.USER_STUDENT_REVIEWER

    test_review_student = "student"
    test_review_reviewer = "reviewer"

    def setUp(self) -> None:
        super(LeaderBoardTest, self).setUp()
        self.set_test_review_status(Review.Status.ASSIGNED)
        self.post_test_review(
            self.test_review_reviewer,
            "review-grade",
            {"scores": "[10, 2]", "is_draft": "false"},
        )

    def test_order_correct(self) -> None:
        response = self.get("student", reverse("leaderboard"))
        ctx = response.context
        self.assertEqual(len(ctx["reviewers_dataset"]), 1)
        self.assertEqual(len(ctx["reviewees_dataset"]), 2)
        self.assertEqual(ctx["reviewees_dataset"][0].id, self.users["student"].id)
        self.assertEqual(ctx["reviewers_dataset"][0].id, self.users["reviewer"].id)
