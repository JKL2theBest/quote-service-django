from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Source, Quote

User = get_user_model()


class QuoteModelTest(TestCase):
    def setUp(self):
        self.source_name = "Тестовый фильм"
        self.source = Source.objects.create(name=self.source_name)

    def test_quote_creation(self):
        initial_quote_count = Quote.objects.count()
        quote = Quote.objects.create(
            text="Это новая тестовая цитата, которая еще не существует в базе.",
            source=self.source,
            weight=150,
        )
        self.assertEqual(Quote.objects.count(), initial_quote_count + 1)
        # Корректируем срез: text[:50]
        self.assertEqual(
            str(quote), '"Это новая тестовая цитата, которая еще не существу..."'
        )

    def test_max_quotes_per_source_validation(self):
        for i in range(3):
            Quote.objects.create(text=f"Цитата номер {i}", source=self.source)
        self.assertEqual(self.source.quotes.count(), 3)
        with self.assertRaises(ValidationError):
            Quote(text="Четвертая лишняя цитата", source=self.source).save()
        self.assertEqual(self.source.quotes.count(), 3)

    def test_unique_quote_text(self):
        Quote.objects.create(text="Уникальный текст", source=self.source)
        with self.assertRaises(ValidationError):
            Quote.objects.create(text="Уникальный текст", source=self.source)


class QuoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.source = Source.objects.create(name="Тестовый источник для API")
        self.quote = Quote.objects.create(
            text="Тестовый текст для API", source=self.source, likes=5, views=10
        )

    def test_random_quote_view(self):
        Quote.objects.all().delete()
        test_quote = Quote.objects.create(
            text="Цитата с 'кавычкой'", source=self.source
        )
        response = self.client.get(reverse("quotes:random_quote"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["quote"], test_quote)
        self.assertContains(response, "Цитата с 'кавычкой'", html=True)

    def test_random_quote_view_no_quotes(self):
        Quote.objects.all().delete()
        Source.objects.all().delete()
        response = self.client.get(reverse("quotes:random_quote"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цитаты еще не добавлены o_0")
        self.assertIsNone(response.context.get("quote"))

    def test_dashboard_view(self):
        response = self.client.get(reverse("quotes:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quotes/dashboard.html")
        expected_keys = ["top_by_likes_page", "top_by_views_page"]
        for key in expected_keys:
            self.assertIn(key, response.context)
        self.assertContains(response, "Топ по просмотрам")

    def test_dashboard_view_no_quotes(self):
        Quote.objects.all().delete()
        Source.objects.all().delete()
        response = self.client.get(reverse("quotes:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цитат с лайками еще нет :'(")

    def test_like_quote_api(self):
        url = reverse("quotes:like_quote", args=[self.quote.id])
        self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.likes, 6)

    def test_dislike_quote_api(self):
        url = reverse("quotes:dislike_quote", args=[self.quote.id])
        self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.dislikes, 1)

    def test_vote_api_non_existent_quote(self):
        non_existent_id = 9999

        like_url = reverse("quotes:like_quote", args=[non_existent_id])
        like_response = self.client.post(
            like_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(like_response.status_code, 404)

        dislike_url = reverse("quotes:dislike_quote", args=[non_existent_id])
        dislike_response = self.client.post(
            dislike_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(dislike_response.status_code, 404)

    def test_vote_api_get_request_not_allowed(self):
        url = reverse("quotes:like_quote", args=[self.quote.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class AdminPanelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            "admin", "admin@test.com", "password"
        )
        self.client.login(username="admin", password="password")
        self.source = Source.objects.create(name="Источник для админки")
        self.quote = Quote.objects.create(text="Цитата для админки", source=self.source)

    def test_source_admin_changelist(self):
        url = reverse("admin:quotes_source_changelist")
        response = self.client.get(url)
        self.assertContains(response, self.source.name)

    def test_quote_admin_changelist(self):
        url = reverse("admin:quotes_quote_changelist")
        response = self.client.get(url)
        self.assertContains(response, "Цитата для админки")


class PaginationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sources = [Source.objects.create(name=f"Источник {i}") for i in range(5)]
        for i in range(1, 16):
            Quote.objects.create(
                text=f"Цитата {i}", source=sources[i % 5], likes=i, views=i * 2
            )
        cls.url = reverse("quotes:dashboard")

    def setUp(self):
        self.client = Client()

    def test_pagination_appears_on_dashboard(self):
        response = self.client.get(self.url)
        self.assertContains(response, '<nav class="pagination"')

    def test_likes_pagination_logic(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["top_by_likes_page"].object_list), 10)
        page1_texts = {q.text for q in response.context["top_by_likes_page"]}
        self.assertIn("Цитата 15", page1_texts)
        self.assertNotIn("Цитата 1", page1_texts)

        response = self.client.get(self.url + "?page_likes=2")
        self.assertEqual(len(response.context["top_by_likes_page"].object_list), 5)
        page2_texts = {q.text for q in response.context["top_by_likes_page"]}
        self.assertIn("Цитата 1", page2_texts)
        self.assertNotIn("Цитата 15", page2_texts)

    def test_views_pagination_logic(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["top_by_views_page"].object_list), 10)

        response = self.client.get(self.url + "?page_views=2")
        self.assertEqual(len(response.context["top_by_views_page"].object_list), 5)

    def test_edge_cases_for_likes_paginator(self):
        response = self.client.get(self.url + "?page_likes=abc")
        self.assertEqual(response.context["top_by_likes_page"].number, 1)
        response = self.client.get(self.url + "?page_likes=999")
        self.assertEqual(response.context["top_by_likes_page"].number, 2)

    def test_edge_cases_for_views_paginator(self):
        response = self.client.get(self.url + "?page_views=abc")
        self.assertEqual(response.context["top_by_views_page"].number, 1)
        response = self.client.get(self.url + "?page_views=999")
        self.assertEqual(response.context["top_by_views_page"].number, 2)
