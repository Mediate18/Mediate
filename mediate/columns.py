from django.urls import reverse_lazy
import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


class ActionColumn(tables.Column):
    def __init__(self, url_name_view, url_name_change, url_name_delete, **kwargs):
        super().__init__(ActionColumn, **kwargs)
        self.url_name_view = url_name_view
        self.url_name_change = url_name_change
        self.url_name_delete = url_name_delete

    def render(self, value):
        html = format_html(
            """
            <div class="text-nowrap">
                <a href="{}">
                    <span class="glyphicon glyphicon-eye-open" data-toggle="tooltip" data-original-title="{}"></span>
                </a>
                <a href="{}">
                    <span class="glyphicon glyphicon-pencil" data-toggle="tooltip" data-original-title="{}"></span>
                    </a>
                <a class="delete-entry" href="" data-toggle="modal" data-target="#deleteModal" modal_url="{}">
                    <span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="{}"></span>
                </a>
            </div>
            """.format(
                reverse_lazy(self.url_name_view, kwargs={'pk': value}),
                _('View'),
                reverse_lazy(self.url_name_change, kwargs={'pk': value}),
                _('Change'),
                reverse_lazy(self.url_name_delete, kwargs={'pk': value}),
                _('Delete'),
            )
        )
        return html


def render_action_column(value, url_name_view, url_name_change, url_name_delete):
    links = """
        <div class="text-nowrap">
    """
    if url_name_view:
        links += """
            <a href="{}">
                <span class="glyphicon glyphicon-eye-open" data-toggle="tooltip" data-original-title="{}"></span>
            </a>
        """.format(reverse_lazy(url_name_view, kwargs={'pk': value}), _('View'))
    if url_name_change:
        links += """
            <a href="{}">
                <span class="glyphicon glyphicon-pencil" data-toggle="tooltip" data-original-title="{}"></span>
            </a>
        """.format(reverse_lazy(url_name_change, kwargs={'pk': value}), _('Change'))
    if url_name_delete:
        links += """
            <a class="delete-entry" href="" data-toggle="modal" data-target="#deleteModal" modal_url="{}">
                <span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="{}"></span>
            </a>
        """.format(reverse_lazy(url_name_delete, kwargs={'pk': value}), _('Delete'))
    links += """
    </div>
    """
    return format_html(links)


