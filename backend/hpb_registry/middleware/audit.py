import threading
from django.utils.deprecation import MiddlewareMixin

# Thread local storage for current user
_thread_locals = threading.local()

def get_current_user():
    """Get the current user from thread local storage"""
    return getattr(_thread_locals, 'user', None)

class AuditMiddleware(MiddlewareMixin):
    """Middleware to track the current user for audit purposes"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            _thread_locals.user = request.user
        else:
            _thread_locals.user = None
    
    def process_response(self, request, response):
        # Clear the thread local after request
        _thread_locals.user = None
        return response
