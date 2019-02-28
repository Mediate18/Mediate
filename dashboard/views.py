from django.shortcuts import render
from django.db.models import Count

from items.models import Item, Manifestation

def view_dashboard(request):
    number_of_manifestations_without_items = Manifestation.objects.annotate(number_of_items=Count('items'))\
        .filter(number_of_items=0).count() or 0
    number_of_manifestations_gt_1_item = Manifestation.objects.annotate(number_of_items=Count('items'))\
                                             .filter(number_of_items__gt=1).count() or 0
    number_of_items_without_manifestations = Item.objects.filter(manifestation__isnull=True).count() or 0
    return render(request, 'dashboard/dashboard.html', {
        'number_of_manifestations_without_items': number_of_manifestations_without_items,
        'number_of_manifestations_gt_1_item': number_of_manifestations_gt_1_item,
        'number_of_items_without_manifestations': number_of_items_without_manifestations
    })
