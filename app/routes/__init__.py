# app/routes/__init__.py
from .UserRoutes import user_bp
from .VectorRoutes import vector_bp
from .FinetuningRoutes import finetuning_bp

__all__ = ['user_bp', 'vector_bp', 'finetuning_bp']