import threading
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

# Thread local storage for current user
_thread_locals = threading.local()

def get_current_user():
    """Get the current user from thread local storage"""
    return getattr(_thread_locals, 'user', None)

def get_current_ip():
    """Get the current IP from thread local storage"""
    return getattr(_thread_locals, 'ip', None)


class AuditMiddleware(MiddlewareMixin):
    """Middleware to track the current user and IP for audit purposes"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            _thread_locals.user = request.user
            _thread_locals.ip = request.META.get('REMOTE_ADDR')
        else:
            _thread_locals.user = None
            _thread_locals.ip = None
    
    def process_response(self, request, response):
        # Clear the thread local after request
        _thread_locals.user = None
        _thread_locals.ip = None
        return response


class AuditLoggingMiddleware(MiddlewareMixin):
    """Middleware to log user actions automatically"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only log for admin and export views
        if not request.user.is_authenticated:
            return None
        
        path = request.path
        
        # Log admin actions
        if path.startswith('/admin/'):
            # Determine action type from path
            if '/add/' in path:
                action = 'add'
            elif '/change/' in path or path.endswith('/change/'):
                action = 'change'
            elif '/delete/' in path:
                action = 'delete'
            else:
                action = 'view'
            
            # Extract model name from path
            parts = path.split('/')
            if len(parts) >= 4:
                model_name = parts[3].capitalize()
            else:
                model_name = 'Unknown'
            
            # Log asynchronously (to avoid blocking)
            self._log_action(request.user, action, model_name, request.META.get('REMOTE_ADDR'))
        
        # Log exports
        elif path.startswith('/export/'):
            self._log_action(request.user, 'export', 'Export', request.META.get('REMOTE_ADDR'))
        
        return None
    
    def _log_action(self, user, action, model_name, ip_address):
        """Create audit log entry"""
        try:
            from users.models import AuditLog
            AuditLog.objects.create(
                user=user,
                action=action,
                model_name=model_name,
                ip_address=ip_address
            )
        except Exception:
            pass  # Fail silently to avoid breaking the request
