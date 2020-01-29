from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import *


class CatalogueModelForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        fields = "__all__"
        widgets = {
            'collection': Select2Widget,
            'transcription': Select2Widget,
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_types_field()
        self.add_related_places_field()

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

    def save(self, commit=True):
        if commit:
            self.save_types()
            self.save_relation_places()
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
                search_fields=['name__icontains']
            ),
        }

    def __init__(self, *args, **kwargs):
        super(LotModelForm, self).__init__(*args, **kwargs)
        self.add_category_field()

    def add_category_field(self):
        self.fields['category'] = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                model=Category,
                search_fields=['bookseller_category__icontains'],
                queryset=Category.objects.filter(catalogue=self.instance.catalogue)),
            queryset=Category.objects.filter(catalogue=self.instance.catalogue),
        )


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
