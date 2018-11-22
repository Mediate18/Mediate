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

    def save(self, commit=True):
        if commit:
            self.save_types()
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


class PersonCatalogueRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonCatalogueRelationRole
        fields = "__all__"


class PersonCollectionRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonCollectionRelation
        fields = "__all__"


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class ParisianCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ParisianCategory
        fields = "__all__"

