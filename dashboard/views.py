from django.shortcuts import render
from django.db.models import Count

from items.models import Item, Edition

def view_dashboard(request):
    if request.user.is_superuser:
        number_of_editions_without_items = Edition.objects.annotate(number_of_items=Count('items'))\
            .filter(number_of_items=0).count() or 0
        number_of_editions_gt_1_item = Edition.objects.annotate(number_of_items=Count('items'))\
                                                 .filter(number_of_items__gt=1).count() or 0
        number_of_items_without_editions = Item.objects.filter(edition__isnull=True).count() or 0
        context = {
            'number_of_editions_without_items': number_of_editions_without_items,
            'number_of_editions_gt_1_item': number_of_editions_gt_1_item,
            'number_of_items_without_editions': number_of_items_without_editions
        }
    else:
        context = {}
    return render(request, 'dashboard/dashboard.html', context)
