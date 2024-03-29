from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from django.contrib.contenttypes.models import ContentType
from .models import *
from catalogues.tools import get_datasets_for_session

from tagme.models import Tag


class CollectionModelForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = "__all__"
        widgets = {
            'catalogue': ModelSelect2MultipleWidget(
                queryset=Catalogue.objects.all(),
                search_fields=['name__icontains'],
            ),
            'transcription': Select2Widget,
        }

    def __init__(self, **kwargs):
        self.datasets = kwargs.pop('datasets', None)
        super().__init__(**kwargs)

        if self.datasets:
            self.fields['catalogue'] = forms.ModelMultipleChoiceField(
                queryset=Catalogue.objects.filter(dataset__in=self.datasets),
                widget=ModelSelect2MultipleWidget(
                    queryset=Catalogue.objects.filter(dataset__in=self.datasets),
                    search_fields=['name__icontains'],
                ),
            )

        self.content_type = ContentType.objects.get_for_model(self.instance)
        self.add_types_field()
        self.add_related_places_field()
        self.add_tag_field()

    def add_types_field(self):
        types = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                    model=CollectionType,
                    search_fields=['name__icontains'],
                ),
            queryset=CollectionType.objects.all(),
            required=False,
            initial=CollectionType.objects.filter(collectioncollectiontyperelation__collection=self.instance)
        )
        self.fields['types'] = types

    def get_collectionplacerelationtype_id(self, type):
        return 'type_' + str(type.uuid) + '_places'

    def add_related_places_field(self):
        for type in CollectionPlaceRelationType.objects.all():
            places = forms.ModelMultipleChoiceField(
                label="{} places".format(type.name).capitalize(),
                widget=ModelSelect2MultipleWidget(
                    model=Place,
                    search_fields=['name__icontains'],
                ),
                queryset=Place.objects.all(),
                required=False,
                initial=Place.objects.filter(related_collections__collection=self.instance, related_collections__type=type)
            )
            self.fields[self.get_collectionplacerelationtype_id(type)] = places

    def add_tag_field(self):
        tag = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                    model=Tag,
                    search_fields=['name__icontains'],
                    # queryset=Tag.objects.filter(namespace='item')
                ),
            queryset=Tag.objects.all(),  # ... filter(namespace='item'),
            required=False,
            initial=Tag.objects.filter(taggedentity__object_id=self.instance.pk,
                                       taggedentity__content_type=self.content_type)
        )
        self.fields['tag'] = tag

    def save(self, commit=True):
        if commit:
            self.save_types()
            self.save_relation_places()
            self.save_tags()
        return super(CollectionModelForm, self).save(commit=commit)

    def save_types(self):
        submitted_types = self.cleaned_data['types']

        # Delete relations for types that are not in the submitted types
        relations_to_delete = CollectionCollectionTypeRelation.objects \
            .filter(collection=self.instance).exclude(type__in=submitted_types)
        for relation in relations_to_delete:
            relation.delete()

        # Add relations for submitted types that are not in the existing types
        new_types = set(submitted_types) - set(CollectionType.objects.filter(
            collectioncollectiontyperelation__collection=self.instance))
        for new_type in new_types:
            collection_collectiontype_relation = CollectionCollectionTypeRelation(collection=self.instance, type=new_type)
            collection_collectiontype_relation.save()

    def save_relation_places(self):
        for type in CollectionPlaceRelationType.objects.all():
            try:
                submitted_related_places = self.cleaned_data[self.get_collectionplacerelationtype_id(type)]
            except KeyError:
                continue

            # Delete places that are not in the submitted places
            related_places_to_delete = CollectionPlaceRelation.objects \
                .filter(collection=self.instance, type=type).exclude(place__in=submitted_related_places)
            for place in related_places_to_delete:
                place.delete()

            # Add submitted places that are not in the existing places
            new_related_places = set(submitted_related_places) - set(Place.objects.filter(
                related_collections__collection=self.instance, related_collections__type=type))
            for new_related_place in new_related_places:
                collection_place_relation = CollectionPlaceRelation(collection=self.instance,
                                                                   place=new_related_place, type=type)
                collection_place_relation.save()

    def save_tags(self):
        tags_in_form = self.cleaned_data['tag']
        existing_tags = Tag.objects.filter(taggedentity__object_id=self.instance.pk,
                                           taggedentity__content_type=self.content_type)

        # Delete tags that were removed in the form
        tags_to_delete = existing_tags.exclude(pk__in=tags_in_form.values_list('pk', flat=True))
        for tag in tags_to_delete:
            TaggedEntity.objects.get(tag=tag, object_id=self.instance.pk, content_type=self.content_type).delete()

        # Add tags that were added in the form
        new_tags = tags_in_form.exclude(pk__in=existing_tags.values_list('pk', flat=True))
        for tag in new_tags:
            self.instance.tags.create(tag=tag)


class CollectionHeldByModelForm(forms.ModelForm):
    class Meta:
        model = CollectionHeldBy
        fields = "__all__"


class CollectionTypeModelForm(forms.ModelForm):
    class Meta:
        model = CollectionType
        fields = "__all__"


class CollectionCollectionTypeRelationModelForm(forms.ModelForm):
    class Meta:
        model = CollectionCollectionTypeRelation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.collections = kwargs.pop('collections', None)
        super().__init__(*args, **kwargs)

        if self.collections:
            self.fields['collection'] = forms.ModelChoiceField(
                queryset=self.collections,
                widget=ModelSelect2Widget(
                    queryset=self.collections,
                    search_fields=['short_title__icontains'],
                ),
            )


class CatalogueModelForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.datasets = kwargs.pop('datasets', None)
        super().__init__(*args, **kwargs)

        if self.datasets:
            self.fields['dataset'] = forms.ModelChoiceField(
                queryset=self.datasets,
                widget=ModelSelect2Widget(
                    queryset=self.datasets,
                    search_fields=['name__icontains']
                )
            )


class CatalogueYearModelForm(forms.ModelForm):
    class Meta:
        model = CatalogueYear
        fields = "__all__"


class LibraryModelForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = "__all__"


class LotModelForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = "__all__"
        widgets = {
            'category': ModelSelect2Widget(
                model=Category,
                search_fields=['bookseller_category__icontains'],
                dependent_fields={'collection': 'collection'}
            )
        }

    def __init__(self, *args, **kwargs):
        self.collections = kwargs.pop('collections', None)
        super().__init__(*args, **kwargs)

        if self.collections:
            self.fields['collection'] = forms.ModelChoiceField(
                queryset=self.collections,
                widget=ModelSelect2Widget(
                    queryset=self.collections,
                    search_fields=['short_title__icontains'],
                    dependent_fields={'category': 'category'}
                ),
            )


class PersonCollectionRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
            ),
            'role': ModelSelect2Widget(
                model=PersonCollectionRelationRole,
                search_fields=['name__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.collections = kwargs.pop('collections', None)
        super().__init__(*args, **kwargs)

        if self.collections:
            self.fields['collection'] = forms.ModelChoiceField(
                queryset=self.collections,
                widget=ModelSelect2Widget(
                    queryset=self.collections,
                    search_fields=['short_title__icontains'],
                ),
            )


class PersonCollectionRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonCollectionRelationRole
        fields = "__all__"


class PersonCatalogueRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCatalogueRelation
        fields = "__all__"
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
            ),
        }

    def __init__(self, **kwargs):
        self.catalogues = kwargs.pop('catalogues', None)
        super().__init__(**kwargs)

        if self.catalogues:
            self.fields['catalogue'] = forms.ModelChoiceField(
                queryset=self.catalogues,
                widget=ModelSelect2Widget(
                    queryset=self.catalogues,
                    search_fields=['name__icontains'],
                ),
            )


class CollectionPlaceRelationModelForm(forms.ModelForm):
    class Meta:
        model = CollectionPlaceRelation
        fields = "__all__"
        widgets = {
            'place': ModelSelect2Widget(
                model=Place,
                search_fields=['name__icontains']
            ),
            'type': ModelSelect2Widget(
                model=CollectionPlaceRelationType,
                search_fields=['name__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.collections = kwargs.pop('collections', None)
        super().__init__(*args, **kwargs)

        if self.collections:
            self.fields['collection'] = forms.ModelChoiceField(
                queryset=self.collections,
                widget=ModelSelect2Widget(
                    queryset=self.collections,
                    search_fields=['short_title__icontains'],
                ),
            )


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        labels = {
            'parent': "Parent category"
        }
        widgets = {
            'parisian_category': ModelSelect2Widget(
                model=ParisianCategory,
                search_fields=['name__icontains', 'description__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.collections = kwargs.pop('collections', None)
        self.categories = kwargs.pop('categories', None)
        super().__init__(*args, **kwargs)

        if self.collections:
            self.fields['collection'] = forms.ModelChoiceField(
                queryset=self.collections,
                widget=ModelSelect2Widget(
                    queryset=self.collections,
                    search_fields=['short_title__icontains'],
                    dependent_fields={'parent': 'category'}
                ),
            )

        if self.categories:
            self.fields['parent'] = forms.ModelChoiceField(
                queryset=self.categories,
                widget=ModelSelect2Widget(
                    attrs={'data-placeholder': "First select a collection"},
                    queryset=self.categories,
                    search_fields=['bookseller_category__icontains'],
                    dependent_fields={'collection': 'collection'}
                ),
            )


class ParisianCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ParisianCategory
        fields = "__all__"


class CollectionPlaceRelationTypeModelForm(forms.ModelForm):
    class Meta:
        model = CollectionPlaceRelationType
        fields = "__all__"


class LotExpandForm(forms.Form):
    number = forms.IntegerField(label='Number')
    prefix = forms.CharField(label='Prefix', max_length=100)


class AddLotBeforeForm(LotModelForm):
    def __init__(self, *args, category=None, page=None, index=None, collection=None, **kwargs):
        super().__init__(*args, **kwargs)
        if category:
            self.fields['category'] = forms.CharField(widget=forms.HiddenInput(), initial=category.uuid)
        if page:
            self.fields['page_in_collection'] = forms.IntegerField(widget=forms.HiddenInput(), initial=page)
        if index:
            self.fields['index_in_collection'] = forms.IntegerField(widget=forms.HiddenInput(), initial=index)
        if collection:
            self.fields['collection'] = forms.CharField(widget=forms.HiddenInput(), initial=collection.uuid)


class AddLotAtEndForm(LotModelForm):
    def __init__(self, *args, category=None, page=None, index=None, collection=None, **kwargs):
        super().__init__(*args, **kwargs)
        if category:
            self.fields['category'] = forms.ModelChoiceField(Category.objects.filter(collection=collection),
                                                             initial=category.uuid)
        if page:
            self.fields['page_in_collection'] = forms.IntegerField(initial=page)
        if index:
            self.fields['index_in_collection'] = forms.IntegerField(widget=forms.HiddenInput(), initial=index)
        if collection:
            self.fields['collection'] = forms.CharField(widget=forms.HiddenInput(), initial=collection.uuid)


class PersonWorkCorrelationForm(forms.Form):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=ModelSelect2Widget(
            attrs={'data-placeholder': "First select a collection"},
            queryset=Person.objects.all(),
            search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
        )
    )
