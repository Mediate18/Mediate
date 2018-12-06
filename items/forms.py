from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget, ModelSelect2MultipleWidget
from apiconnectors.widgets import ApiSelectWidget
from .models import *

from tagging.models import Tag


class BookFormatModelForm(forms.ModelForm):
    class Meta:
        model = BookFormat
        fields = "__all__"


class ItemModelForm(forms.ModelForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_tag_field()

    def add_tag_field(self):
        tag = forms.ModelMultipleChoiceField(
            widget=ModelSelect2MultipleWidget(
                    model=Tag,
                    search_fields=['name__icontains'],
                    # queryset=Tag.objects.filter(namespace='item')
                ),
            queryset=Tag.objects.all(),  # ... filter(namespace='item'),
            required=False,
            initial=self.instance.tags
        )
        self.fields['tag'] = tag

    class Meta:
        model = Item
        fields = "__all__"
        widgets = {
            'collection': Select2Widget,
            'lot': ModelSelect2Widget(
                model=Lot,
                search_fields=['lot_as_listed_in_catalogue__icontains']
            ),
            'manifestation': ModelSelect2Widget(
                model=Manifestation,
                search_fields=['place__name__icontains', 'year__icontains']
            ),
            'book_format': Select2Widget,
            'binding_material_details': Select2Widget,
            'language': Select2Widget,
            'work': Select2Widget,
        }

    def save(self, commit=True):
        self.instance.tags = self.cleaned_data['tag']
        return super(ItemModelForm, self).save(commit=commit)


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


class PersonItemRelationRoleModelForm(forms.ModelForm):
    class Meta:
        model = PersonItemRelationRole
        fields = "__all__"


class ManifestationModelForm(forms.ModelForm):
    class Meta:
        model = Manifestation
        fields = "__all__"
        widgets = {
            'item': ModelSelect2Widget(
                model=Item,
                search_fields=['short_title__icontains']
            ),
        }


class PublisherModelForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"


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



