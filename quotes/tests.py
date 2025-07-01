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
            weight=150
        )
        self.assertEqual(quote.source.name, self.source_name)
        self.assertEqual(Quote.objects.count(), initial_quote_count + 1)
        self.assertEqual(str(quote), '"Это новая тестовая цитата, которая еще не существу..."')

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
        self.client = Client()
        self.source = Source.objects.create(name="Тестовый источник")
        self.quote = Quote.objects.create(text="Тестовый текст", source=self.source, likes=5)

    def test_random_quote_view(self):
        """Тест главной страницы."""
        response = self.client.get(reverse('quotes:random_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/random_quote.html')

        self.assertIn('quote', response.context)
        quote_in_context = response.context['quote']
        self.assertIsInstance(quote_in_context, Quote)

        self.assertContains(response, quote_in_context.text)

    def test_random_quote_view_no_quotes(self):
        """Тест главной страницы, когда нет цитат."""
        Quote.objects.all().delete()
        response = self.client.get(reverse('quotes:random_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Цитаты еще не добавлены")

    def test_top_quotes_view(self):
        """Тест страницы с топом цитат."""
        response = self.client.get(reverse('quotes:top_quotes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/top_quotes.html')
        self.assertContains(response, "Тестовый текст")

    def test_top_quotes_view_no_quotes(self):
        """Тест страницы топа, когда нет цитат."""
        Quote.objects.all().delete()
        response = self.client.get(reverse('quotes:top_quotes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пока нет ни одной цитаты с лайками.")

    def test_like_quote_api(self):
        """Тест API для лайков."""
        self.assertEqual(self.quote.likes, 5)
        url = reverse('quotes:like_quote', args=[self.quote.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.likes, 6)
        self.assertEqual(response.json()['likes'], 6)

    def test_dislike_quote_api(self):
        """Тест API для дизлайков."""
        self.assertEqual(self.quote.dislikes, 0)
        url = reverse('quotes:dislike_quote', args=[self.quote.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.dislikes, 1)
        self.assertEqual(response.json()['dislikes'], 1)

    def test_vote_api_non_existent_quote(self):
        """Тест голосования за несуществующую цитату."""
        like_url = reverse('quotes:like_quote', args=[999])
        dislike_url = reverse('quotes:dislike_quote', args=[999])
        
        response_like = self.client.post(like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_like.status_code, 404)
        
        response_dislike = self.client.post(dislike_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_dislike.status_code, 404)
        
    def test_vote_api_get_request_not_allowed(self):
        """Тест: GET запросы к API голосования запрещены."""
        url = reverse('quotes:like_quote', args=[self.quote.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

class AdminPanelTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.login(username='admin', password='password')
        
        self.source = Source.objects.create(name="Источник для админки")
        self.quote = Quote.objects.create(text="Цитата для админки", source=self.source)

    def test_source_admin_changelist(self):
        """Тест страницы списка источников в админке."""
        url = reverse('admin:quotes_source_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.source.name)
        self.assertContains(response, '1')

    def test_quote_admin_changelist(self):
        """Тест страницы списка цитат в админке."""
        url = reverse('admin:quotes_quote_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Цитата для админки')

    def test_quote_admin_short_text(self):
        """Тест метода short_text в админке."""
        long_text = "Это очень длинный текст, который определенно должен быть усечен в административной панели для удобства отображения."
        long_quote = Quote.objects.create(text=long_text, source=self.source)
        
        url = reverse('admin:quotes_quote_changelist')
        response = self.client.get(url)

        self.assertContains(response, "...")
        self.assertContains(response, long_text[:10])
        self.assertNotContains(response, long_text)