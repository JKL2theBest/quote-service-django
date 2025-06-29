from django.shortcuts import render
import random
from django.db.models import F
from .models import Quote
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

def random_quote_view(request):
    """
    View для отображения случайной цитаты с учетом веса.
    """
    quotes_with_weights = list(Quote.objects.values_list('id', 'weight'))

    if not quotes_with_weights:
        return render(request, 'quotes/random_quote.html', {'quote': None})

    quote_ids, weights = zip(*quotes_with_weights)

    random_quote_id = random.choices(quote_ids, weights=weights, k=1)[0]

    Quote.objects.filter(pk=random_quote_id).update(views=F('views') + 1)

    quote = Quote.objects.get(pk=random_quote_id)

    context = {
        'quote': quote,
    }
    return render(request, 'quotes/random_quote.html', context)

@require_POST
def like_quote(request, quote_id):
    """Обработка лайка."""
    try:
        quote_qs = Quote.objects.filter(pk=quote_id)
        if not quote_qs.exists():
            raise Http404("Quote not found")

        quote_qs.update(likes=F('likes') + 1)

        updated_quote = quote_qs.first()
        return JsonResponse({'likes': updated_quote.likes, 'dislikes': updated_quote.dislikes})

    except Quote.DoesNotExist: # Избыточно, но пусть будет
        raise Http404("Quote not found")

@require_POST
def dislike_quote(request, quote_id):
    """Обработка дизлайка."""
    try:
        quote_qs = Quote.objects.filter(pk=quote_id)
        if not quote_qs.exists():
            raise Http404("Quote not found")

        quote_qs.update(dislikes=F('dislikes') + 1)

        updated_quote = quote_qs.first()
        return JsonResponse({'likes': updated_quote.likes, 'dislikes': updated_quote.dislikes})
        
    except Quote.DoesNotExist:
        raise Http404("Quote not found")