from django.core.cache import cache
from .models import Product, Category


def get_products_by_category(category_id):
    """
    Сервисная функция для получения продуктов по категории
    С использованием низкоуровневого кеширования
    """
    cache_key = f'products_category_{category_id}'
    products = cache.get(cache_key)

    if products is None:
        try:
            category = Category.objects.get(id=category_id)
            products = Product.objects.filter(
                category=category,
                is_published=True
            ).select_related('category', 'owner').order_by('-created_at')

            # Кешируем результат на 10 минут
            cache.set(cache_key, products, 60 * 10)
        except Category.DoesNotExist:
            products = []

    return products


def get_all_categories_with_products_count():
    """
    Сервисная функция для получения всех категорий с количеством продуктов
    """
    cache_key = 'categories_with_counts'
    categories = cache.get(cache_key)

    if categories is None:
        categories = Category.objects.annotate(
            products_count=models.Count('products', filter=models.Q(products__is_published=True))
        ).order_by('name')
        cache.set(cache_key, categories, 60 * 30)  # 30 минут

    return categories