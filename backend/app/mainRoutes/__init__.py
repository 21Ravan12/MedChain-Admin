# app/MainRoutes/__init__.py

from .auth import auth_bp  # Auth blueprint'i import et
from .admin import auth_ad  # Admin blueprint'i import et

__all__ = ['auth_bp','auth_ad']      # Dışa aktarılacakları belirt