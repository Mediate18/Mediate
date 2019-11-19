from collections import OrderedDict
from django import forms
from django.contrib.contenttypes.models import ContentType
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from apiconnectors.widgets import ApiSelectWidget
from .models import *

from tagme.models import Tag
from betterforms.multiform import MultiModelForm


class BookFormatModelForm(forms.ModelForm):
    class Meta:
        model = BookFormat
        fields = "__all__"


class ItemModelForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_type = ContentType.objects.get_for_model(self.instance)
        self.add_tag_field()
        self.add_languages_field()
        self.add_publishers_field()

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

    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            'collection': Select2Widget,
            'lot': ModelSelect2Widget(
                model=Lot,
                search_fields=['lot_as_listed_in_catalogue__icontains']
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

    def save(self, commit=True):
        self.instance = super(ItemModelForm, self).save(commit=commit)
        if commit:
            self.save_tags()
            self.save_languages()
            self.save_publishers()

        return self.instance


class ItemAuthorModelForm(forms.ModelForm):
    class Meta:
        model = ItemAuthor
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
        }


class ItemItemTypeRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemItemTypeRelation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
        }


class ItemLanguageRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemLanguageRelation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
            'language': ModelSelect2Widget(
                model=Language,
                search_fields=['name__icontains']
            )
        }


class ItemMaterialDetailsRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemMaterialDetailsRelation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
        }


class ItemTypeModelForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = "__all__"


class ItemWorkRelationModelForm(forms.ModelForm):
    class Meta:
        model = ItemWorkRelation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
            'work': ModelSelect2Widget(
                model=Work,
                search_fields=['title__icontains']
            )
        }


class ItemWorkRelationAddForm(forms.ModelForm):
    viaf_select_id = 'viaf_id'  # ID of the VIAF suggest widget

    class Meta:
        model = Work
        fields = ['viaf_id', 'title']
        widgets = {
            'viaf_id': ApiSelectWidget(
                url='workandviaf_suggest',
                attrs={'data-html': True, 'data-placeholder': "Search for a work - <i>italic: works in the local database</i>"},
            ),
        }

    class Media:
        js = ('js/viaf_select.js',)



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
        fields = "__all__"
        widgets = {
            'person': ModelSelect2Widget(
                model=Person,
                search_fields=['short_name__icontains']
            ),
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
            'role': ModelSelect2Widget(
                model=PersonItemRelationRole,
                search_fields=['name__icontains']
            )
        }


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
        fields = ['person', 'role']
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
        widgets = {
            'viaf_id': ApiSelectWidget(
                url=reverse_lazy('work_viaf_suggest'),
                attrs={'data-html': True,
                       'data-placeholder': "Search for a work"},
            ),
        }

    class Media:
        js = ('js/viaf_select.js',)


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
            'collection': Select2Widget,
            'lot': ModelSelect2Widget(
                model=Lot,
                search_fields=['lot_as_listed_in_catalogue__icontains']
            ),
            'book_format': Select2Widget,
            'binding_material_details': Select2Widget,
            'language': Select2Widget,
            'work': Select2Widget,
        }


class ItemAndEditionForm(MultiModelForm):
    form_classes = OrderedDict([
        ('item', ItemModelForm2),
        ('edition', EditionModelForm)
    ])
