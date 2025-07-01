from django.shortcuts import render
import random
from django.db.models import F
from .models import Quote
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie # <-- 1. Импортируем

@ensure_csrf_cookie
def random_quote_view(request):
    """
    View для отображения случайной цитаты с учетом веса.
    """
    quotes_with_weights = list(Quote.objects.values_list("id", "weight"))

    if not quotes_with_weights:
        return render(request, "quotes/random_quote.html", {"quote": None})

    quote_ids, weights = zip(*quotes_with_weights)
    random_quote_id = random.choices(quote_ids, weights=weights, k=1)[0]
    Quote.objects.filter(pk=random_quote_id).update(views=F("views") + 1)
    quote = Quote.objects.get(pk=random_quote_id)

    context = {
        "quote": quote,
    }
    return render(request, "quotes/random_quote.html", context)


@require_POST
def like_quote(request, quote_id):
    """Обработка лайка."""
    updated_quote = Quote.objects.filter(pk=quote_id).update_and_get(likes=F("likes") + 1)

    if updated_quote is None:
        raise Http404("Quote not found")

    return JsonResponse(
        {"likes": updated_quote.likes, "dislikes": updated_quote.dislikes}
    )


@require_POST
def dislike_quote(request, quote_id):
    """Обработка дизлайка."""
    updated_quote = Quote.objects.filter(pk=quote_id).update_and_get(dislikes=F("dislikes") + 1)

    if updated_quote is None:
        raise Http404("Quote not found")

    return JsonResponse(
        {"likes": updated_quote.likes, "dislikes": updated_quote.dislikes}
    )


def top_quotes_view(request):
    """
    Отображение 10 самых популярных цитат (по лайкам).
    """
    top_quotes = Quote.objects.select_related("source").order_by("-likes")[:10]

    context = {
        "quotes": top_quotes,
    }

    return render(request, "quotes/top_quotes.html", context)
