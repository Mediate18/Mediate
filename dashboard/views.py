from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.template import Template, Context

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
    # books_with_parisian_category = Item.objects\
    #     .filter(lot__collection__in=collections, non_book=False, parisian_category__isnull=False).distinct().count()

    context = {
        # 'books_with_parisian_category': books_with_parisian_category,
        # 'percentage_books_with_parisian_category': round(100 * books_with_parisian_category/book_items)

    }

    return render(request, 'dashboard/totals.html', context)

def collection_count(request):
    collections_for_session = get_collections_for_session(request)
    return HttpResponse (str(collections_for_session.distinct().count()))


def get_bookitems_count(collection_ids):
    uncountable_book_items_count = Item.objects.filter(lot__collection_id__in=collection_ids,
                                                       uncountable_book_items=True).count()
    book_items = Item.objects.filter(lot__collection_id__in=collection_ids, non_book=False).count() \
                 + uncountable_book_items_count
    return book_items, uncountable_book_items_count


def bookitems_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    book_items, uncountable_book_items_count = get_bookitems_count(collection_ids)
    non_book_items = Item.objects.filter(lot__collection_id__in=collection_ids, non_book=True).count()
    percentage_non_book_items = round(100 * non_book_items/book_items, 1)

    template = Template("""
        <span>{{ book_items }}{% if uncountable_book_items_count %}+{% endif %}</span>
        <span id="non_book_items" hx-swap-oob="true">{{ non_book_items }}</span>
        <span id="percentage_non_book_items" hx-swap-oob="true">({{ percentage_non_book_items }}% of total)</span>
    """)

    context = Context({
        'book_items': book_items,
        'uncountable_book_items_count': uncountable_book_items_count,
        'non_book_items': non_book_items,
        'percentage_non_book_items': percentage_non_book_items,
    })

    return HttpResponse(template.render(context))


def work_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    works = Work.objects.filter(items__item__lot__collection_id__in=collection_ids).distinct().count()
    return HttpResponse(works)


def person_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    persons = PersonItemRelation.objects.filter(collection_id__in=collection_ids).values_list('person_id').distinct().count()
    female_persons = Person.objects.filter(sex=Person.FEMALE,
                                           personitemrelation__item__lot__collection_id__in=collection_ids)\
                                    .distinct().count()

    template = Template("""
        <span>{{ persons }}</span>
        <span id="female_persons" hx-swap-oob="true">{{ female_persons }}</span>
    """)

    context = Context({
        'persons': persons,
        'female_persons': female_persons,
    })

    return HttpResponse(template.render(context))


def country_city_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    cities_of_publication = list(Place.objects
                                 .filter(publicationplace__edition__items__lot__collection_id__in=collection_ids)
                                 .distinct().values_list('uuid', flat=True))
    cities_of_birth = list(Place.objects.filter(persons_born__personitemrelation__item__lot__collection_id__in=collection_ids)
                           .distinct().values_list('uuid', flat=True))
    cities_of_death = list(Place.objects.filter(persons_died__personitemrelation__item__lot__collection_id__in=collection_ids)
                           .distinct().values_list('uuid', flat=True))
    cities_list = list(set(cities_of_publication+cities_of_birth+cities_of_death))
    cities = len(cities_list)
    countries = Country.objects.filter(place__in=cities_list).distinct().count()

    template = Template("""
        <span>{{ countries }}</span>
        <span id="cities" hx-swap-oob="true">{{ cities }}</span>
    """)

    context = Context({
        'countries': countries,
        'cities': cities,
    })

    return HttpResponse(template.render(context))


def language_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    languages = Language.objects\
        .annotate(item_cnt=Count('items', filter=Q(items__item__lot__collection_id__in=collection_ids,
                                                   items__item__non_book=False)))\
        .filter(item_cnt__gt=0).distinct().count()
    return HttpResponse(languages)


def itempersonrelation_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    item_person_relations = PersonItemRelation.objects.filter(item__lot__collection_id__in=collection_ids,
                                                              item__non_book=False).values('item').distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_item_person_relations = round(100 * item_person_relations / book_items)

    template = Template("""
        <span>{{ item_person_relations }}</span>
        <span id="percentage_item_person_relations" hx-swap-oob="true">({{percentage_item_person_relations}}% of total number of book Items)</span>
    """)
    context = Context({
        'item_person_relations': item_person_relations,
        'percentage_item_person_relations': percentage_item_person_relations,
    })
    return HttpResponse(template.render(context))


def itemworkrelation_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    item_work_relations = ItemWorkRelation.objects.filter(item__lot__collection_id__in=collection_ids,
                                                          item__non_book=False).distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_item_work_relations = round(100 * item_work_relations/book_items)

    template = Template("""
            <span>{{ item_work_relations }}</span>
            <span id="percentage_item_work_relations" hx-swap-oob="true">({{percentage_item_work_relations}}% of total number of book Items)</span>
        """)
    context = Context({
        'item_work_relations': item_work_relations,
        'percentage_item_work_relations': percentage_item_work_relations,
    })
    return HttpResponse(template.render(context))


def itemswithdate_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    items_with_date = Item.objects.filter(lot__collection_id__in=collection_ids, edition__year_start__isnull=False,
                                          non_book=False).distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_items_with_date = round(100 * items_with_date/book_items)

    template = Template("""
                <span>{{ items_with_date }}</span>
                <span id="percentage_items_with_date" hx-swap-oob="true">({{percentage_items_with_date}}% of total number of book Items)</span>
            """)
    context = Context({
        'items_with_date': items_with_date,
        'percentage_items_with_date': percentage_items_with_date,
    })
    return HttpResponse(template.render(context))


def itemswithplaceofpublication_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    items_with_place_of_publication = Item.objects.filter(lot__collection_id__in=collection_ids,
                                                          edition__publicationplace__place__isnull=False,
                                                          non_book=False).distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_items_with_place_of_publication = round(100 * items_with_place_of_publication/book_items)

    template = Template("""
                    <span>{{ items_with_place_of_publication }}</span>
                    <span id="percentage_items_with_place_of_publication" hx-swap-oob="true">({{percentage_items_with_place_of_publication}}% of total number of book Items)</span>
                """)
    context = Context({
        'items_with_place_of_publication': items_with_place_of_publication,
        'percentage_items_with_place_of_publication': percentage_items_with_place_of_publication,
    })
    return HttpResponse(template.render(context))


def itemswithpublisher_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    items_with_publisher = Item.objects.filter(edition__publisher__isnull=False).distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_items_with_publisher = round(100 * items_with_publisher/book_items)

    template = Template("""
                        <span>{{ items_with_publisher }}</span>
                        <span id="percentage_items_with_publisher" hx-swap-oob="true">({{percentage_items_with_publisher}}% of total number of book Items)</span>
                    """)
    context = Context({
        'items_with_publisher': items_with_publisher,
        'percentage_items_with_publisher': percentage_items_with_publisher,
    })
    return HttpResponse(template.render(context))


def personswithplaceofbirth_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    persons_with_place_of_birth = Person.objects.filter(city_of_birth__isnull=False).distinct().count()
    persons = PersonItemRelation.objects.filter(collection_id__in=collection_ids).values_list('person_id').distinct().count()
    percentage_persons_with_place_of_birth = round(100 * persons_with_place_of_birth / persons)

    template = Template("""
                            <span>{{ persons_with_place_of_birth }}</span>
                            <span id="percentage_persons_with_place_of_birth" hx-swap-oob="true">({{percentage_persons_with_place_of_birth}}% of total number of persons)</span>
                        """)
    context = Context({
        'persons_with_place_of_birth': persons_with_place_of_birth,
        'percentage_persons_with_place_of_birth': percentage_persons_with_place_of_birth,
    })
    return HttpResponse(template.render(context))


def personswithplaceofdeath_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    persons_with_place_of_death = Person.objects.filter(city_of_death__isnull=False).distinct().count()
    persons = PersonItemRelation.objects.filter(collection_id__in=collection_ids).values_list('person_id').distinct().count()
    percentage_persons_with_place_of_death = round(100 * persons_with_place_of_death / persons)

    template = Template("""
                            <span>{{ persons_with_place_of_death }}</span>
                            <span id="percentage_persons_with_place_of_death" hx-swap-oob="true">({{percentage_persons_with_place_of_death}}% of total number of persons)</span>
                        """)
    context = Context({
        'persons_with_place_of_death': persons_with_place_of_death,
        'percentage_persons_with_place_of_death': percentage_persons_with_place_of_death,
    })
    return HttpResponse(template.render(context))


def bookswithlanguage_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    books_with_language = Item.objects.filter(lot__collection_id__in=collection_ids, languages__isnull=False, non_book=False) \
            .distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_books_with_language = round(100 * books_with_language/book_items)

    template = Template("""
                            <span>{{ books_with_language }}</span>
                            <span id="percentage_books_with_language" hx-swap-oob="true">({{percentage_books_with_language}}% of total number of book Items)</span>
                        """)
    context = Context({
        'books_with_language': books_with_language,
        'percentage_books_with_language': percentage_books_with_language,
    })
    return HttpResponse(template.render(context))


def bookswithparisiancategory_count(request):
    collection_ids = list(get_collections_for_session(request).values_list('uuid', flat=True))
    books_with_parisian_category = Item.objects \
            .filter(lot__collection_id__in=collection_ids, non_book=False, parisian_category__isnull=False).distinct().count()
    book_items, _ = get_bookitems_count(collection_ids)
    percentage_books_with_parisian_category = round(100 * books_with_parisian_category/book_items)

    template = Template("""
                            <span>{{ books_with_parisian_category }}</span>
                            <span id="percentage_books_with_parisian_category" hx-swap-oob="true">({{percentage_books_with_parisian_category}}% of total number of book Items)</span>
                        """)
    context = Context({
        'books_with_parisian_category': books_with_parisian_category,
        'percentage_books_with_parisian_category': percentage_books_with_parisian_category,
    })
    return HttpResponse(template.render(context))