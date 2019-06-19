from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext_lazy as _
import os
import mimetypes
from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy


@permission_required('global.view_all')
def protected_media(request, filename):
    """
    View to send file via X-Sendfile
    :param request: the HTTP request
    :param filename: the filename, extracted from the url
    :return: a HttpResponse object
    """
    # Construct full path and base name
    full_path = os.path.join(settings.MEDIA_ROOT, filename)
    base_name = os.path.basename(filename)

    # Check whether the file exist
    if not os.path.exists(full_path):
        raise Http404(_("The requested file does not exist"))

    # Let Django serve it if the XSENDFILE setting is false
    if not settings.XSENDFILE:
        from django.views.static import serve
        return serve(request, full_path, document_root='/')

    # Determine the mime type
    (mime_type, encoding) = mimetypes.guess_type(full_path)

    # Construct the response
    response = HttpResponse(content_type=mime_type)
    response['Content-Disposition'] = 'inline;filename='+base_name
    response['X-Sendfile'] = full_path

    return response


class GenericDetailView(DetailView):
    """
    A DetailView that uses a generic detail template and lists object field-value pairs
    given by the class field 'object_fields'.
    """
    template_name = 'generic_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()
        context['object_name'] = self.model.__name__

        if hasattr(self, 'object_fields'):
            context['object_dict'] = dict([(field.replace('_', ' '), getattr(obj, field))
                                           for field in self.object_fields])

        context['edit_url'] = reverse_lazy('change_' + self.model.__name__.lower(), args=[obj.pk])
        return context
