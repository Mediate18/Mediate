from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from django.contrib.contenttypes.models import ContentType
from .models import *

from tagme.models import Tag


class CatalogueModelForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = "__all__"
        widgets = {
            'collection': ModelSelect2Widget(
                queryset=Collection.objects.all(),
                search_fields=['name__icontains'],
            ),
            'transcription': Select2Widget,
        }

    def __init__(self, **kwargs):
        self.dataset = kwargs.pop('dataset', None)
        super().__init__(**kwargs)

        if self.dataset:
            self.fields['collection'] = forms.ModelChoiceField(
                queryset=Collection.objects.filter(dataset=self.dataset),
                widget=ModelSelect2Widget(
                    queryset=Collection.objects.filter(dataset=self.dataset),
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
                    model=CatalogueType,
                    search_fields=['name__icontains'],
                ),
            queryset=CatalogueType.objects.all(),
            required=False,
            initial=CatalogueType.objects.filter(cataloguecataloguetyperelation__catalogue=self.instance)
        )
        self.fields['types'] = types

    def get_catalogueplacerelationtype_id(self, type):
        return 'type_' + str(type.uuid) + '_places'

    def add_related_places_field(self):
        for type in CataloguePlaceRelationType.objects.all():
            places = forms.ModelMultipleChoiceField(
                label="{} places".format(type.name).capitalize(),
                widget=ModelSelect2MultipleWidget(
                    model=Place,
                    search_fields=['name__icontains'],
                ),
                queryset=Place.objects.all(),
                required=False,
                initial=Place.objects.filter(related_catalogues__catalogue=self.instance, related_catalogues__type=type)
            )
            self.fields[self.get_catalogueplacerelationtype_id(type)] = places

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
        return super(CatalogueModelForm, self).save(commit=commit)

    def save_types(self):
        submitted_types = self.cleaned_data['types']

        # Delete relations for types that are not in the submitted types
        relations_to_delete = CatalogueCatalogueTypeRelation.objects \
            .filter(catalogue=self.instance).exclude(type__in=submitted_types)
        for relation in relations_to_delete:
            relation.delete()

        # Add relations for submitted types that are not in the existing types
        new_types = set(submitted_types) - set(CatalogueType.objects.filter(
            cataloguecataloguetyperelation__catalogue=self.instance))
        for new_type in new_types:
            catalogue_cataloguetype_relation = CatalogueCatalogueTypeRelation(catalogue=self.instance, type=new_type)
            catalogue_cataloguetype_relation.save()

    def save_relation_places(self):
        for type in CataloguePlaceRelationType.objects.all():
            try:
                submitted_related_places = self.cleaned_data[self.get_catalogueplacerelationtype_id(type)]
            except KeyError:
                continue

            # Delete places that are not in the submitted places
            related_places_to_delete = CataloguePlaceRelation.objects \
                .filter(catalogue=self.instance, type=type).exclude(place__in=submitted_related_places)
            for place in related_places_to_delete:
                place.delete()

            # Add submitted places that are not in the existing places
            new_related_places = set(submitted_related_places) - set(Place.objects.filter(
                related_catalogues__catalogue=self.instance, related_catalogues__type=type))
            for new_related_place in new_related_places:
                catalogue_place_relation = CataloguePlaceRelation(catalogue=self.instance,
                                                                     place=new_related_place, type=type)
                catalogue_place_relation.save()

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


class CatalogueHeldByModelForm(forms.ModelForm):
    class Meta:
        model = CatalogueHeldBy
        fields = "__all__"


class CatalogueTypeModelForm(forms.ModelForm):
    class Meta:
        model = CatalogueType
        fields = "__all__"


class CatalogueCatalogueTypeRelationModelForm(forms.ModelForm):
    class Meta:
        model = CatalogueCatalogueTypeRelation
        fields = "__all__"


class CollectionModelForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionYearModelForm(forms.ModelForm):
    class Meta:
        model = CollectionYear
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
            'catalogue': ModelSelect2Widget(
                model=Catalogue,
                search_fields=['short_title__icontains'],
                dependent_fields={'category': 'category'}
            ),
            'category': ModelSelect2Widget(
                model=Category,
                search_fields=['bookseller_category__icontains'],
                dependent_fields={'catalogue': 'catalogue'}
            )
        }


class PersonCatalogueRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCatalogueRelation
        fields = "__all__"
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
            ),
            'catalogue': ModelSelect2Widget(
                model=Catalogue,
                search_fields=['short_title__icontains']
            ),
            'role': ModelSelect2Widget(
                model=PersonCatalogueRelationRole,
                search_fields=['name__icontains']
            )
        }


class PersonCatalogueRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonCatalogueRelationRole
        fields = "__all__"


class PersonCollectionRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


class CataloguePlaceRelationModelForm(forms.ModelForm):
    class Meta:
        model = CataloguePlaceRelation
        fields = "__all__"
        widgets = {
            'catalogue': ModelSelect2Widget(
                model=Catalogue,
                search_fields=['short_title__icontains']
            ),
            'place': ModelSelect2Widget(
                model=Place,
                search_fields=['name__icontains']
            ),
            'type': ModelSelect2Widget(
                model=CataloguePlaceRelationType,
                search_fields=['name__icontains']
            )
        }


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        labels = {
            'parent': "Parent category"
        }


class ParisianCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ParisianCategory
        fields = "__all__"


class CataloguePlaceRelationTypeModelForm(forms.ModelForm):
    class Meta:
        model = CataloguePlaceRelationType
        fields = "__all__"


class LotExpandForm(forms.Form):
    number = forms.IntegerField(label='Number')
    prefix = forms.CharField(label='Prefix', max_length=100)


class AddLotBeforeForm(LotModelForm):
    def __init__(self, *args, category=None, page=None, index=None, catalogue=None, **kwargs):
        super().__init__(*args, **kwargs)
        if category:
            self.fields['category'] = forms.CharField(widget=forms.HiddenInput(), initial=category.uuid)
        if page:
            self.fields['page_in_catalogue'] = forms.IntegerField(widget=forms.HiddenInput(), initial=page)
        if index:
            self.fields['index_in_catalogue'] = forms.IntegerField(widget=forms.HiddenInput(), initial=index)
        if catalogue:
            self.fields['catalogue'] = forms.CharField(widget=forms.HiddenInput(), initial=catalogue.uuid)


class AddLotAtEndForm(LotModelForm):
    def __init__(self, *args, category=None, page=None, index=None, catalogue=None, **kwargs):
        super().__init__(*args, **kwargs)
        if category:
            self.fields['category'] = forms.ModelChoiceField(Category.objects.filter(catalogue=catalogue),
                                                             initial=category.uuid)
        if page:
            self.fields['page_in_catalogue'] = forms.IntegerField(initial=page)
        if index:
            self.fields['index_in_catalogue'] = forms.IntegerField(widget=forms.HiddenInput(), initial=index)
        if catalogue:
            self.fields['catalogue'] = forms.CharField(widget=forms.HiddenInput(), initial=catalogue.uuid)
