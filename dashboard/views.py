from django.shortcuts import render
from django.db.models import Count

from items.models import Item, Edition, Work, Language, PersonItemRelation, ItemWorkRelation
from catalogues.models import Lot, Catalogue
from persons.models import Place, Person, Country

def view_dashboard(request):
    if request.user.is_superuser:
        number_of_editions_without_items = Edition.objects.annotate(number_of_items=Count('items'))\
            .filter(number_of_items=0).count() or 0
        number_of_editions_gt_1_item = Edition.objects.annotate(number_of_items=Count('items'))\
                                                 .filter(number_of_items__gt=1).count() or 0
        number_of_items_without_editions = Item.objects.filter(edition__isnull=True).count() or 0

        number_of_items_without_lot = Item.objects.filter(lot__isnull=True).count() or 0
        number_of_lots_without_items = Lot.objects.annotate(number_of_items=Count('item')).filter(number_of_items=0)\
            .count() or 0

        context = {
            'number_of_editions_without_items': number_of_editions_without_items,
            'number_of_editions_gt_1_item': number_of_editions_gt_1_item,
            'number_of_items_without_editions': number_of_items_without_editions,
            'number_of_items_without_lot': number_of_items_without_lot,
            'number_of_lots_without_items': number_of_lots_without_items
        }
    else:
        context = {}
    return render(request, 'dashboard/dashboard.html', context)


def view_totals(request):
    """
    Create a view with counts for a selection of models
    :param request:
    :return:
    """
    catalogues = Catalogue.objects.count()
    book_items = Item.objects.filter(non_book=False).count()
    non_book_items = Item.objects.filter(non_book=True).count()
    works = Work.objects.count()
    persons = Person.objects.count()
    female_persons = Person.objects.filter(sex=Person.FEMALE).count()

    cities_of_publication = list(Place.objects.filter(edition__isnull=False).distinct().values_list('uuid', flat=True))
    cities_of_birth = list(Place.objects.filter(persons_born__isnull=False).distinct().values_list('uuid', flat=True))
    cities_of_death = list(Place.objects.filter(persons_born__isnull=False).distinct().values_list('uuid', flat=True))
    cities_list = list(set(cities_of_publication+cities_of_birth+cities_of_death))
    cities = len(cities_list)
    countries = Country.objects.filter(place__in=cities_list).distinct().count()

    languages = Language.objects.annotate(item_cnt=Count('items')).filter(item_cnt__gt=0).count()

    item_person_relations = PersonItemRelation.objects.count()

    context = {
        'catalogues': catalogues,
        'book_items': book_items,
        'non_book_items': non_book_items,
        'percentage_non_book_items': round(100 * non_book_items/book_items, 1),
        'works': works,
        'persons': persons,
        'female_persons': female_persons,
        'countries': countries,
        'cities': cities,
        'languages': languages,

        'item_person_relations': item_person_relations,
        'percentage_item_person_relations': round(100 * item_person_relations/book_items),

    }

    return render(request, 'dashboard/totals.html', context)
