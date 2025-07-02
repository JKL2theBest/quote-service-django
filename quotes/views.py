from django.shortcuts import render
import random
from django.db.models import F, Count, Sum
from .models import Quote, Source
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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
    updated_quote = Quote.objects.filter(pk=quote_id).update_and_get(
        likes=F("likes") + 1
    )

    if updated_quote is None:
        raise Http404("Quote not found")

    return JsonResponse(
        {"likes": updated_quote.likes, "dislikes": updated_quote.dislikes}
    )


@require_POST
def dislike_quote(request, quote_id):
    """Обработка дизлайка."""
    updated_quote = Quote.objects.filter(pk=quote_id).update_and_get(
        dislikes=F("dislikes") + 1
    )

    if updated_quote is None:
        raise Http404("Quote not found")

    return JsonResponse(
        {"likes": updated_quote.likes, "dislikes": updated_quote.dislikes}
    )


def dashboard_view(request):
    """
    Отображение дашборда.
    """
    kpi_stats = Quote.objects.aggregate(
        total_quotes=Count('id'),
        total_likes=Sum('likes'),
        total_views=Sum('views')
    )
    total_sources = Source.objects.count()

    top_by_likes_list = Quote.objects.select_related("source").order_by("-likes")
    top_by_views_list = Quote.objects.select_related("source").order_by("-views")
    most_recent = Quote.objects.select_related("source").order_by("-created_at")[:5]

    paginator_likes = Paginator(top_by_likes_list, 10)
    paginator_views = Paginator(top_by_views_list, 10)

    page_likes_num = request.GET.get('page_likes')
    page_views_num = request.GET.get('page_views')

    try:
        top_by_likes_page = paginator_likes.page(page_likes_num)
    except PageNotAnInteger:
        top_by_likes_page = paginator_likes.page(1)
    except EmptyPage:
        top_by_likes_page = paginator_likes.page(paginator_likes.num_pages)

    try:
        top_by_views_page = paginator_views.page(page_views_num)
    except PageNotAnInteger:
        top_by_views_page = paginator_views.page(1)
    except EmptyPage:
        top_by_views_page = paginator_views.page(paginator_views.num_pages)

    context = {
        'total_quotes': kpi_stats.get('total_quotes', 0),
        'total_likes': kpi_stats.get('total_likes', 0) or 0,
        'total_views': kpi_stats.get('total_views', 0) or 0,
        'total_sources': total_sources,
        'top_by_likes_page': top_by_likes_page,
        'top_by_views_page': top_by_views_page,
        'most_recent': most_recent,
    }

    return render(request, "quotes/dashboard.html", context)