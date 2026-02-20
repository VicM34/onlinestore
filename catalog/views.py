from django.shortcuts import render, get_object_or_404
from .models import Product, Contact


def home(request):
    """Контроллер для главной страницы"""
    # Получаем все товары из базы данных, сортируем по дате создания (новые сверху)
    products = Product.objects.all().order_by('-created_at')
    
    # Для допзадания: вывод в консоль последних 5 продуктов
    latest_products = products[:5]
    print("Последние 5 продуктов:")
    for product in latest_products:
        print(f"  - {product.name} ({product.created_at})")

    context = {
        'products': products,  # Передаем все товары в шаблон
        'latest_products': latest_products,  # Для допзадания
    }
    return render(request, 'catalog/home.html', context)


def contacts(request):
    """Страница контактов"""
    success_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Сохраняем в базу данных
        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        success_message = "Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время."

    # Получаем все сохраненные контакты для отображения
    all_contacts = Contact.objects.all().order_by('-created_at')

    context = {
        'success_message': success_message,
        'contacts': all_contacts,
    }
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