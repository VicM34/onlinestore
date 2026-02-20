from django.shortcuts import render, get_object_or_404
from .models import Product  # Добавляем импорт модели Product


def home(request):
    """Контроллер для главной страницы"""
    # Получаем все товары из базы данных, сортируем по дате создания (новые сверху)
    products = Product.objects.all().order_by('-created_at')

    context = {
        'products': products  # Передаем товары в шаблон
    }
    return render(request, 'catalog/home.html', context)


def contacts(request):
    """Контроллер для страницы контактов"""
    context = {}

    if request.method == 'POST':
        # Обработка данных формы
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Для демонстрации просто добавим сообщение
        context['success_message'] = f'Спасибо, {name}! Ваше сообщение отправлено.'

    return render(request, 'catalog/contacts.html', context)


def product_detail(request, pk):
    """
    Контроллер для страницы одного товара
    Принимает pk (primary key) товара
    """
    # Получаем товар по его ID или возвращаем 404 если не найден
    product = get_object_or_404(Product, pk=pk)

    context = {
        'product': product  # Передаем товар в шаблон
    }
    return render(request, 'catalog/product_detail.html', context)