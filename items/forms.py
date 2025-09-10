from collections import OrderedDict
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from .models import *
from catalogues.models import Category, ParisianCategory
from catalogues.views.views import get_collections_for_session

from tagme.models import Tag
from dal import autocomplete


class BookFormatModelForm(forms.ModelForm):
    class Meta:
        model = BookFormat
        fields = "__all__"


class ItemModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.catalogues = kwargs.pop('catalogues', None)
        self.lots = kwargs.pop('lots', None)
        super().__init__(*args, **kwargs)

        if self.catalogues is not None and self.catalogues.exists():
            self.fields['catalogue'] = forms.ModelChoiceField(
                queryset=self.catalogues,
                widget=ModelSelect2Widget(
                    queryset=self.catalogues,
                    search_fields=['name__icontains'],
                ),
            )

        if self.lots is not None and self.lots.exists():
            self.fields['lot'] = forms.ModelChoiceField(
                queryset=self.lots,
                widget=ModelSelect2Widget(
                    queryset=self.lots,
                    search_fields=['lot_as_listed_in_collection__icontains'],
                ),
            )
        
        super().__init__(**kwargs)
        self.content_type = ContentType.objects.get_for_model(self.instance)
        self.add_tag_field()
        self.add_languages_field()
        self.add_publishers_field()
        self.add_material_details_field()
        self.add_itemtype_field()

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

    def add_languages_field(self):
        languages = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                model=Language,
                search_fields=['name__icontains', 'language_code_2char__iexact', 'language_code_3char__iexact'],
            ),
            queryset=Language.objects.all(),
            required=False,
            initial=Language.objects.filter(items__item=self.instance)
        )
        self.fields['languages'] = languages

    def add_publishers_field(self):
        publishers = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                model=Person,
                search_fields=['short_name__icontains', 'first_names__icontains', 'surname__icontains'],
            ),
            queryset=Person.objects.all(),
            required=False,
            initial=Person.objects.filter(publisher__edition__items=self.instance)
        )
        self.fields['publishers'] = publishers
        
    def add_material_details_field(self):
        material_details = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                model=MaterialDetails,
                search_fields=['description']
            ),
            queryset=MaterialDetails.objects.all(),
            required=False,
            initial=MaterialDetails.objects.filter(items__item=self.instance)
        )
        self.fields['material_details'] = material_details

    def add_itemtype_field(self):
        itemtypes = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                model=ItemType,
                search_fields=['name']
            ),
            queryset=ItemType.objects.all(),
            required=False,
            initial=ItemType.objects.filter(itemitemtyperelation__item=self.instance)
        )
        self.fields['item_type'] = itemtypes

    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            'catalogue': Select2Widget,
            'lot': ModelSelect2Widget(
                model=Lot,
                search_fields=['lot_as_listed_in_collection__icontains']
            ),
            'edition': ModelSelect2Widget(
                model=Edition,
                search_fields=['place__name__icontains', 'year__icontains']
            ),
            'book_format': Select2Widget,
            'binding_material_details': Select2Widget,
            'language': Select2Widget,
            'work': Select2Widget,
        }

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

    def save_languages(self):
        languages_in_form = self.cleaned_data['languages']
        existing_languages = Language.objects.filter(items__item=self.instance)

        # Delete languages that were removed in the form
        languages_to_delete = existing_languages.exclude(pk__in=languages_in_form.values_list('pk', flat=True))
        for language in languages_to_delete:
            ItemLanguageRelation.objects.get(item=self.instance, language=language).delete()

        # Add languages taht were added in the form
        new_languages = languages_in_form.exclude(pk__in=existing_languages.values_list('pk', flat=True))
        for language in new_languages:
            item = self.instance
            ItemLanguageRelation(item=item, language=language).save()
            
    def save_publishers(self):
        persons_in_form = self.cleaned_data['publishers']
        existing_persons = Person.objects.filter(publisher__edition__items=self.instance)

        # Delete publishers that were removed in the form
        persons_to_delete = existing_persons.exclude(pk__in=persons_in_form.values_list('pk', flat=True))
        for person in persons_to_delete:
            Publisher.objects.get(edition__items=self.instance, publisher=person).delete()

        # Add publishers that were added in the form
        new_persons = persons_in_form.exclude(pk__in=existing_persons.values_list('pk', flat=True))
        for person in new_persons:
            item = self.instance
            Publisher(edition=item.edition, publisher=person).save()
            
    def save_material_details(self):
        material_details_in_form = self.cleaned_data['material_details']
        existing_material_details = MaterialDetails.objects.filter(items__item=self.instance)

        # Delete material details that were removed in the form
        material_details_to_delete = existing_material_details\
            .exclude(pk__in=material_details_in_form.values_list('pk', flat=True))
        for material_details in material_details_to_delete:
            ItemMaterialDetailsRelation.objects.get(item=self.instance, material_details=material_details).delete()

        # Add material details that were added in the form
        new_material_details = material_details_in_form\
            .exclude(pk__in=existing_material_details.values_list('pk', flat=True))
        for material_details in new_material_details:
            ItemMaterialDetailsRelation(item=self.instance, material_details=material_details).save()

    def save_itemtypes(self):
        itemtypes_in_form = self.cleaned_data['item_type']
        existing_itemtypes = ItemType.objects.filter(itemitemtyperelation__item=self.instance)

        # Delete item types that were removed in the form
        itemtypes_to_delete = existing_itemtypes.exclude(pk__in=itemtypes_in_form.values_list('pk', flat=True))
        for itemtype in itemtypes_to_delete:
            ItemItemTypeRelation.objects.get(item=self.instance, type=itemtype).delete()

        # Add item types that were added in the form
        new_itemtypes = itemtypes_in_form.exclude(pk__in=existing_itemtypes.values_list('pk', flat=True))
        for itemtype in new_itemtypes:
            ItemItemTypeRelation(item=self.instance, type=itemtype).save()

    def save(self, commit=True):
        self.instance = super(ItemModelForm, self).save(commit=commit)
        if commit:
            self.save_tags()
            self.save_languages()
            self.save_publishers()
            self.save_material_details()
            self.save_itemtypes()

        return self.instance


class ItemSuggest(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Item.objects.filter(lot__collection__in=get_collections_for_session(self.request))

        if self.q:
            qs = qs.filter(short_title__icontains=self.q)

        return qs


class ItemAuthorModelForm(forms.ModelForm):
    class Meta:
        model = ItemAuthor
        fields = "__all__"
        widgets = {
            'author': ModelSelect2Widget(
                queryset=Person.objects.all(),
                search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        super().__init__(*args, **kwargs)

        if self.items is not None:
            self.fields['item'] = forms.ModelChoiceField(
                queryset=self.items,
                widget=autocomplete.ModelSelect2(
                    url='item_suggest',
                    attrs={'data-placeholder': "Search for an item", 'data-minimum-input-length': 3},
                )
            )


class ItemItemTypeRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemItemTypeRelation
        fields = "__all__"
        widgets = {
            'itemtype': ModelSelect2Widget(
                model=ItemType,
                search_fields=['name__icontains']
            ),
        }

    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        super().__init__(*args, **kwargs)

        if self.items is not None:
            self.fields['item'] = forms.ModelChoiceField(
                queryset=self.items,
                widget=autocomplete.ModelSelect2(
                    url='item_suggest',
                    attrs={'data-placeholder': "Search for an item", 'data-minimum-input-length': 3},
                )
            )


class ItemLanguageRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemLanguageRelation
        fields = "__all__"
        widgets = {
            'language': ModelSelect2Widget(
                model=Language,
                search_fields=['name__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        super().__init__(*args, **kwargs)

        if self.items is not None:
            self.fields['item'] = forms.ModelChoiceField(
                queryset=self.items,
                widget=autocomplete.ModelSelect2(
                    url='item_suggest',
                    attrs={'data-placeholder': "Search for an item", 'data-minimum-input-length': 3},
                )
            )


class ItemMaterialDetailsRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemMaterialDetailsRelation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        super().__init__(*args, **kwargs)

        if self.items is not None:
            self.fields['item'] = forms.ModelChoiceField(
                queryset=self.items,
                widget=autocomplete.ModelSelect2(
                    url='item_suggest',
                    attrs={'data-placeholder': "Search for an item", 'data-minimum-input-length': 3},
                )
            )


class ItemTypeModelForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = "__all__"


class ItemWorkRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemWorkRelation
        fields = "__all__"
        widgets = {
            'work': ModelSelect2Widget(
                model=Work,
                search_fields=['title__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        super().__init__(*args, **kwargs)

        if self.items is not None:
            self.fields['item'] = forms.ModelChoiceField(
                queryset=self.items,
                widget=autocomplete.ModelSelect2(
                    url='item_suggest',
                    attrs={'data-placeholder': "Search for an item", 'data-minimum-input-length': 3},
                )
            )


class ItemWorkRelationAddForm(forms.ModelForm):
    viaf_select_id = 'viaf_id'  # ID of the VIAF suggest widget

    class Meta:
        model = Work
        fields = ['viaf_id', 'title']

    class Media:
        js = ()


class LanguageModelForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = "__all__"


class MaterialDetailsModelForm(forms.ModelForm):
    class Meta:
        model = MaterialDetails
        fields = "__all__"


class PersonItemRelationModelForm(forms.ModelForm):
    class Meta:
        model = PersonItemRelation
        fields = ['item', 'person', 'role', 'notes']
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'role': ModelSelect2Widget(
                model=PersonItemRelationRole,
                search_fields=['name__icontains']
            )
        }

    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        super().__init__(*args, **kwargs)

        if self.items is not None:
            self.fields['item'] = forms.ModelChoiceField(
                queryset=self.items,
                widget=autocomplete.ModelSelect2(
                    url='item_suggest',
                    attrs={'data-placeholder': "Search for an item", 'data-minimum-input-length': 3},
                )
            )


class AddAnotherWidget(ModelSelect2Widget):
    def render(self, *args, **kwargs):
        output = super(AddAnotherWidget, self).render(*args, **kwargs)
        output += '&nbsp;&nbsp;' \
                  '<a href="#" data-toggle="modal" data-target="#addanotherModal">' \
                  '<span class="glyphicon glyphicon-plus" data-toggle="tooltip" data-original-title="Add another">' \
                  '</span>' \
                  '</a>'
        return output


class PersonItemRelationAddForm(forms.ModelForm):
    viaf_select_id = 'viaf_id'  # ID of the VIAF suggest widget

    class Meta:
        model = PersonItemRelation
        fields = ['person', 'role', 'notes']
        widgets = {
            'person': AddAnotherWidget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'role': ModelSelect2Widget(
                model=PersonItemRelationRole,
                search_fields=['name__icontains']
            )
        }

    class Media:
        js = ('js/viaf_select.js',)


class EditionPlaceForm(forms.ModelForm):
    class Meta:
        model = Edition
        fields = ['place']
        widgets = {
            'place': ModelSelect2Widget(
                model=Place,
                search_fields=['name__icontains']
            )
        }


class ItemFormatForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['book_format']
        widgets = {
            'book_format': ModelSelect2Widget(
                model=BookFormat,
                search_fields=['name__icontains']
            )
        }


class ItemLanguageForm(forms.ModelForm):
    class Meta:
        model = ItemLanguageRelation
        fields = ['language']
        widgets = {
            'language': ModelSelect2MultipleWidget(
                model=Language,
                search_fields=['name__icontains', 'language_code_2char__iexact', 'language_code_3char__iexact']
            )
        }


class ItemItemTypeForm(forms.ModelForm):
    class Meta:
        model = ItemItemTypeRelation
        fields = ['type']
        widgets = {
            'type': ModelSelect2MultipleWidget(
                model=ItemType,
                search_fields=['name__icontains']
            )
        }


class ItemTagsForm(forms.ModelForm):
    class Meta:
        model = TaggedEntity
        fields = ['tag']
        widgets = {
            'tag': ModelSelect2MultipleWidget(
                model=Tag,
                search_fields=['name__icontains']
            )
        }


class ItemWorksForm(forms.ModelForm):
    class Meta:
        model = ItemWorkRelation
        fields = ['work']
        widgets = {
            'work': ModelSelect2MultipleWidget(
                model=Work,
                search_fields=['title__icontains']
            )
        }


class ItemMaterialDetailsForm(forms.ModelForm):
    class Meta:
        model = ItemMaterialDetailsRelation
        fields = ['material_details']
        widgets = {
            'material_details': ModelSelect2MultipleWidget(
                model=MaterialDetails,
                search_fields=['description__icontains']    
            )
        }


class ItemParisianCategoriesForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['parisian_category']
        widgets = {
            'parisian_category': ModelSelect2Widget(
                model=ParisianCategory,
                search_fields=['name__icontains', 'description__icontains']
            )
        }


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['publisher']
        widgets = {
            'publisher': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains', 'surname__icontains', 'first_names__icontains']
            )
        }


class PersonItemRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonItemRelationRole
        fields = "__all__"


class EditionPlacesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_publicationplaces_field()

    def add_publicationplaces_field(self):
        publication_places = forms.ModelMultipleChoiceField(
            label=_("Real places of publication"),
            widget=ModelSelect2MultipleWidget(
                model=Place,
                search_fields=['name__icontains']
            ),
            queryset=Place.objects.all(),
            required=False,
        )
        self.fields['publication_places'] = publication_places


class EditionModelForm(forms.ModelForm):
    class Meta:
        model = Edition
        fields = "__all__"
        widgets = {
            'place': ModelSelect2Widget(
                model=Place,
                search_fields=['name__icontains']
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_publicationplaces_field()

    def add_publicationplaces_field(self):
        publication_places = forms.ModelMultipleChoiceField(
            label=_("Real places of publication"),
            widget=ModelSelect2MultipleWidget(
                model=Place,
                search_fields=['name__icontains']
            ),
            queryset=Place.objects.all(),
            required=False,
            initial=Place.objects.filter(publicationplace__edition=self.instance)
        )
        self.fields['publication_places'] = publication_places

    def save_publicationplaces(self):
        places_in_form = self.cleaned_data['publication_places']
        existing_places = Place.objects.filter(publicationplace__edition=self.instance)

        # Delete places that were remove in the form
        places_to_delete = existing_places.exclude(pk__in=places_in_form.values_list('pk', flat=True))
        for place in places_to_delete:
            PublicationPlace.objects.get(edition=self.instance, place=place).delete()

        # Add places that were added in the form
        new_places = places_in_form.exclude(pk__in=existing_places.values_list('pk', flat=True))
        for place in new_places:
            PublicationPlace.objects.create(edition=self.instance, place=place)

    def save(self, commit=True):
        self.instance = super().save(commit=commit)
        if commit:
            self.save_publicationplaces()

        return self.instance


class PublisherModelForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"
        widgets = {
            'publisher': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'edition': ModelSelect2Widget(
                model=Edition,
                search_fields=['year__icontains', 'place__name__icontains']
            )
        }


class SubjectModelForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = "__all__"


class WorkModelForm(forms.ModelForm):
    viaf_select_id = 'viaf_id'

    class Meta:
        model = Work
        fields = ['viaf_id', 'title']


class WorkAuthorModelForm(forms.ModelForm):
    class Meta:
        model = WorkAuthor
        fields = "__all__"
        widgets = {
            'author': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'work': ModelSelect2Widget(
                model=Work,
                search_fields=['title__icontains']
            ),
        }


class WorkSubjectModelForm(forms.ModelForm):
    class Meta:
        model = WorkSubject
        fields = "__all__"


class ItemModelForm2(ItemModelForm):
    class Meta:
        model = Item
        exclude = ['edition']
        widgets = {
            'book_format': Select2Widget,
            'binding_material_details': Select2Widget,
            'language': Select2Widget,
            'work': Select2Widget,
        }


class CombinedFormBase(forms.Form):
    form_classes = OrderedDict([])

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None) or {}
        super().__init__(*args, **kwargs)
        self.forms = {}
        for name, form_class in self.form_classes.items():
            form = form_class(*args, **kwargs, instance=instance.get(name, None))
            self.forms[name] = form
            self.initial.update(form.initial)

    @property
    def fields(self):
        fields = {}
        for name, form in self.forms.items():
            fields.update(form.fields)
        return fields

    @fields.setter
    def fields(self, new_fields):
        pass

    def is_valid(self):
        isValid = True
        for name, form in self.forms.items():
            if not form.is_valid():
                isValid = False
        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        if not super().is_valid() :
            isValid = False
        for name, form in self.forms.items():
            self.errors.update(form.errors)
        return isValid

    def clean(self):
        cleaned_data = super().clean()
        for name, form in self.forms.items():
            cleaned_data.update(form.cleaned_data)
        return cleaned_data


class ItemAndEditionForm(CombinedFormBase):
    form_classes = OrderedDict([
        ('item', ItemModelForm2),
        ('edition', EditionModelForm)
    ])

    def __init__(self, *args, **kwargs):
        self.catalogues = kwargs.pop('catalogues', None)
        self.lots = kwargs.pop('lots', None)
        super().__init__(*args, **kwargs)

        if self.catalogues is not None and self.catalogues.exists():
            self.forms['item'].fields['catalogue'] = forms.ModelChoiceField(
                queryset=self.catalogues,
                widget=ModelSelect2Widget(
                    queryset=self.catalogues,
                    search_fields=['name__icontains'],
                ),
            )

        if self.lots is not None and self.lots.exists():
            self.forms['item'].fields['lot'] = forms.ModelChoiceField(
                queryset=self.lots,
                widget=ModelSelect2Widget(
                    queryset=self.lots,
                    search_fields=['lot_as_listed_in_collection__icontains'],
                ),
            )
