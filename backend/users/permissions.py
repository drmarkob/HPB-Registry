from functools import wraps
from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            
            # Superusers bypass all checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if hasattr(request.user, 'profile'):
                user_role = request.user.profile.role
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("You don't have permission to access this page")
        return wrapped
    return decorator

def can_export(view_func):
    """Check if user can export data"""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        
        # Superusers can always export
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if hasattr(request.user, 'profile'):
            if request.user.profile.has_permission('export'):
                return view_func(request, *args, **kwargs)
        
        return HttpResponseForbidden("You don't have permission to export data")
    return wrapped
