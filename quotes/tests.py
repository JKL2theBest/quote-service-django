from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Source, Quote

User = get_user_model()


class QuoteModelTest(TestCase):

    def setUp(self):
        """Настройка тестовых данных для каждого теста в этом классе."""
        self.source_name = "Тестовый фильм"
        self.source = Source.objects.create(name=self.source_name)
        self.assertEqual(str(self.source), self.source_name)

    def test_quote_creation(self):
        """Тест создания цитаты."""
        initial_quote_count = Quote.objects.count()
        self.assertGreater(initial_quote_count, 0)

        quote = Quote.objects.create(
            text="Это новая тестовая цитата, которая еще не существует.",
            source=self.source,
            weight=150,
        )
        self.assertEqual(quote.source.name, self.source_name)
        self.assertEqual(Quote.objects.count(), initial_quote_count + 1)
        self.assertEqual(
            str(quote), '"Это новая тестовая цитата, которая еще не существу..."'
        )

    def test_max_quotes_per_source_validation(self):
        """Тест: не более 3 цитат на источник."""
        for i in range(3):
            Quote.objects.create(text=f"Цитата номер {i}", source=self.source)

        self.assertEqual(self.source.quotes.count(), 3)
        with self.assertRaises(ValidationError):
            Quote(text="Четвертая лишняя цитата", source=self.source).save()
        self.assertEqual(self.source.quotes.count(), 3)

    def test_unique_quote_text(self):
        """Тест уникальности текста цитаты."""
        Quote.objects.create(text="Уникальный текст", source=self.source)
        with self.assertRaises(ValidationError):
            Quote.objects.create(text="Уникальный текст", source=self.source)


class QuoteViewTest(TestCase):

    def setUp(self):
        """
        Настройка тестовых данных.
        """
        self.client = Client()
        self.source = Source.objects.create(name="Тестовый источник для API")
        self.quote = Quote.objects.create(
            text="Тестовый текст для API", source=self.source, likes=5
        )

    def test_random_quote_view(self):
        """Тест главной страницы с данными."""
        Quote.objects.all().delete()

        test_quote = Quote.objects.create(
            text="Цитата с 'кавычкой'",
            source=self.source
        )
        
        response = self.client.get(reverse('quotes:random_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/random_quote.html')

        self.assertEqual(response.context['quote'], test_quote)
        
        self.assertContains(response, "Цитата с 'кавычкой'", html=True)

    def test_random_quote_view_no_quotes(self):
        """Тест главной страницы, когда в БД нет цитат."""
        Quote.objects.all().delete()
        Source.objects.all().delete()

        response = self.client.get(reverse("quotes:random_quote"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Цитаты еще не добавлены")

        self.assertIn("quote", response.context)
        self.assertIsNone(response.context["quote"])

    def test_dashboard_view(self):
        """Тест страницы дашборда со статистикой."""
        self.assertGreater(Quote.objects.count(), 1)
        url = reverse('quotes:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/dashboard.html')

        expected_keys = [
            'total_quotes', 'total_likes', 'total_views', 'total_sources',
            'top_by_likes_page',
            'top_by_views_page',
            'most_recent'
        ]
        for key in expected_keys:
            self.assertIn(key, response.context)

        self.assertEqual(response.context["total_quotes"], Quote.objects.count())
        self.assertEqual(response.context["total_sources"], Source.objects.count())

        self.assertContains(response, "Топ-10 по просмотрам")
        self.assertContains(response, "5 последних добавленных")
        self.assertContains(response, "Всего цитат")

    def test_dashboard_view_no_quotes(self):
        """Тест страницы дашборда, когда в БД нет цитат."""
        Quote.objects.all().delete()
        Source.objects.all().delete()

        url = reverse("quotes:dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_quotes"], 0)
        self.assertEqual(response.context["total_likes"], 0)
        self.assertEqual(response.context["total_views"], 0)
        self.assertContains(response, "Цитат с лайками еще нет.")

    def test_like_quote_api(self):
        """Тест API для лайков."""
        initial_likes = self.quote.likes
        url = reverse("quotes:like_quote", args=[self.quote.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 200)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.likes, initial_likes + 1)
        self.assertEqual(response.json()["likes"], initial_likes + 1)

    def test_dislike_quote_api(self):
        """Тест API для дизлайков."""
        initial_dislikes = self.quote.dislikes
        url = reverse("quotes:dislike_quote", args=[self.quote.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 200)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.dislikes, initial_dislikes + 1)
        self.assertEqual(response.json()["dislikes"], initial_dislikes + 1)

    def test_vote_api_non_existent_quote(self):
        """Тест голосования за несуществующую цитату."""
        non_existent_id = 9999
        like_url = reverse("quotes:like_quote", args=[non_existent_id])
        dislike_url = reverse("quotes:dislike_quote", args=[non_existent_id])

        response_like = self.client.post(
            like_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response_like.status_code, 404)

        response_dislike = self.client.post(
            dislike_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response_dislike.status_code, 404)

    def test_vote_api_get_request_not_allowed(self):
        """Тест: GET запросы к API голосования запрещены."""
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
        """Тест страницы списка источников в админке."""
        url = reverse("admin:quotes_source_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.source.name)
        self.assertContains(response, "1")

    def test_quote_admin_changelist(self):
        """Тест страницы списка цитат в админке."""
        url = reverse("admin:quotes_quote_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цитата для админки")

    def test_quote_admin_short_text(self):
        """Тест метода short_text в админке."""
        long_text = "Это очень длинный текст, который определенно должен быть усечен в административной панели для удобства отображения."
        Quote.objects.create(text=long_text, source=self.source)

        url = reverse("admin:quotes_quote_changelist")
        response = self.client.get(url)

        self.assertContains(response, "...")
        self.assertContains(response, long_text[:10])
        self.assertNotContains(response, long_text)


class PaginationTest(TestCase):
    def setUp(self):
        Quote.objects.all().delete()
        Source.objects.all().delete()
        
        self.client = Client()
        sources = [Source.objects.create(name=f"Источник для пагинации {i}") for i in range(5)]
        
        for i in range(15):
            Quote.objects.create(
                text=f"Цитата для пагинации номер {i}",
                source=sources[i % 5],
                likes=i,
            )

    def test_pagination_appears_on_dashboard(self):
        response = self.client.get(reverse('quotes:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<nav class="pagination"')

    def test_first_page_content(self):
        response = self.client.get(reverse('quotes:dashboard'))
        self.assertEqual(len(response.context['top_by_likes_page'].object_list), 10)
        self.assertContains(response, "Цитата для пагинации номер 14")
        self.assertNotContains(response, "Цитата для пагинации номер 4")

    def test_second_page_content(self):
        response = self.client.get(reverse('quotes:dashboard') + '?page_likes=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['top_by_likes_page'].object_list), 5)
        self.assertContains(response, "Цитата для пагинации номер 4")
        self.assertNotContains(response, "Цитата для пагинации номер 5")

    def test_invalid_page_number_handled(self):
        response = self.client.get(reverse('quotes:dashboard') + '?page_likes=abc')
        self.assertEqual(response.context['top_by_likes_page'].number, 1)

    def test_out_of_range_page_handled(self):
        response = self.client.get(reverse('quotes:dashboard') + '?page_likes=999')
        self.assertEqual(response.context['top_by_likes_page'].number, 2)

    def test_out_of_range_page_for_views_list(self):
        quote = Quote.objects.first()
        quote.views = 10
        quote.save()
        
        response = self.client.get(reverse('quotes:dashboard') + '?page_views=999')
        self.assertEqual(response.context['top_by_views_page'].number, 2)