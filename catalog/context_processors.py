from django.core.cache import cache
from .models import Category
from django.db import models


def categories_processor(request):
    """Контекстный процессор для передачи категорий во все шаблоны"""
    cache_key = 'nav_categories'
    categories = cache.get(cache_key)

    if categories is None:
        categories = Category.objects.annotate(
            products_count=models.Count('products', filter=models.Q(products__is_published=True))
        ).order_by('name')
        cache.set(cache_key, categories, 60 * 30)  # 30 минут

    return {'categories': categories}