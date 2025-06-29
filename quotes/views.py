from django.shortcuts import render
import random
from django.db.models import F
from .models import Quote

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