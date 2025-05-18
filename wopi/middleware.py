from django.utils.deprecation import MiddlewareMixin
import socket

class LocalRemoteUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        hostip = socket.gethostbyname(socket.gethostname())
        ip = request.META.get('REMOTE_ADDR')
        #if ip.startswith('192.168.') or ip == '127.0.0.1':
        if ip == hostip or ip == '127.0.0.1':
            request.is_local = True
        else:
            request.is_local = False
