class SetRemoteAddrMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            request.META['REMOTE_ADDR'] = x_forwarded_for.split(',')[0].strip()
        return self.get_response(request)