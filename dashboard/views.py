from django.shortcuts import render, redirect
from django.db.models import Count, Q

from items.models import Item, Edition, Work, Language, PersonItemRelation, ItemWorkRelation
from catalogues.models import Lot, Collection
from catalogues.views.views import get_collections_for_session
from persons.models import Place, Person, Country


def view_dashboard(request):
    if request.user.has_perm('catalogues.change_dataset'):
        return render(request, 'dashboard/dashboard.html', {})
    return redirect('about')


def get_dashboard_stats(request):
    if request.user.is_superuser:
        number_of_editions_without_items = Edition.objects\
                                               .filter(items__lot__collection__in=get_collections_for_session(request))\
                                               .annotate(number_of_items=Count('items'))\
                                               .filter(number_of_items=0).count() or 0
        number_of_editions_gt_1_item = Edition.objects\
                                           .filter(items__lot__collection__in=get_collections_for_session(request))\
                                           .annotate(number_of_items=Count('items'))\
                                           .filter(number_of_items__gt=1).count() or 0
        number_of_items_without_editions = Item.objects.filter(lot__collection__in=get_collections_for_session(request),
                                                               edition__isnull=True).count() or 0

        number_of_items_without_lot = Item.objects.filter(lot__collection__in=get_collections_for_session(request),
                                                          lot__isnull=True).count() or 0
        number_of_lots_without_items = Lot.objects\
                                           .filter(collection__in=get_collections_for_session(request))\
                                           .annotate(number_of_items=Count('item')).filter(number_of_items=0)\
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
    return render(request, 'dashboard/dashboard_stats.html', context)


def view_totals(request):
    """
    Create a view with counts for a selection of models
    :param request:
    :return:
    """
    collections_for_session = get_collections_for_session(request)
    collections = list(collections_for_session)
    collections_count = collections_for_session.distinct().count()
    uncountable_book_items_count = Item.objects.filter(lot__collection__in=collections,
                                                       uncountable_book_items=True).count()
    book_items = Item.objects.filter(lot__collection__in=collections, non_book=False).count() \
                 + uncountable_book_items_count
    non_book_items = Item.objects.filter(lot__collection__in=collections, non_book=True).count()
    works = Work.objects.filter(items__item__lot__collection__in=collections).distinct().count()
    persons = Person.objects.filter(personitemrelation__item__lot__collection__in=collections).distinct().count()
    female_persons = Person.objects.filter(sex=Person.FEMALE,
                                           personitemrelation__item__lot__collection__in=collections)\
                                    .distinct().count()

    cities_of_publication = list(Place.objects
                                 .filter(publicationplace__edition__items__lot__collection__in=collections)
                                 .distinct().values_list('uuid', flat=True))
    cities_of_birth = list(Place.objects.filter(persons_born__personitemrelation__item__lot__collection__in=collections)
                           .distinct().values_list('uuid', flat=True))
    cities_of_death = list(Place.objects.filter(persons_died__personitemrelation__item__lot__collection__in=collections)
                           .distinct().values_list('uuid', flat=True))
    cities_list = list(set(cities_of_publication+cities_of_birth+cities_of_death))
    cities = len(cities_list)
    countries = Country.objects.filter(place__in=cities_list).distinct().count()

    languages = Language.objects\
        .annotate(item_cnt=Count('items', filter=Q(items__item__lot__collection__in=collections,
                                                   items__item__non_book=False)))\
        .filter(item_cnt__gt=0).distinct().count()

    item_person_relations = PersonItemRelation.objects.filter(item__lot__collection__in=collections,
                                                              item__non_book=False).values('item').distinct().count()
    item_work_relations = ItemWorkRelation.objects.filter(item__lot__collection__in=collections,
                                                          item__non_book=False).distinct().count()
    items_with_date = Item.objects.filter(lot__collection__in=collections, edition__year_start__isnull=False,
                                          non_book=False).distinct().count()
    items_with_place_of_publication = Item.objects.filter(lot__collection__in=collections, edition__place__isnull=False,
                                                          non_book=False).distinct().count()

    persons_with_place_of_birth = Person.objects.filter(city_of_birth__isnull=False).distinct().count()
    persons_with_place_of_death = Person.objects.filter(city_of_death__isnull=False).distinct().count()

    books_with_language = Item.objects.filter(lot__collection__in=collections, languages__isnull=False, non_book=False)\
        .distinct().count()

    context = {
        'collections': collections_count,
        'book_items': book_items,
        'uncountable_book_items_count': uncountable_book_items_count,
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
        'item_work_relations': item_work_relations,
        'percentage_item_work_relations': round(100 * item_work_relations/book_items),
        'items_with_date': items_with_date,
        'percentage_items_with_date': round(100 * items_with_date/book_items),
        'items_with_place_of_publication': items_with_place_of_publication,
        'percentage_items_with_place_of_publication': round(100 * items_with_place_of_publication/book_items),

        'persons_with_place_of_birth': persons_with_place_of_birth,
        'percentage_persons_with_place_of_birth': round(100 * persons_with_place_of_birth / persons),
        'persons_with_place_of_death': persons_with_place_of_death,
        'percentage_persons_with_place_of_death': round(100 * persons_with_place_of_death/persons),

        'books_with_language': books_with_language,
        'percentage_books_with_language': round(100 * books_with_language/book_items)

    }

    return render(request, 'dashboard/totals.html', context)
