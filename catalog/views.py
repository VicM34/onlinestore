from django.shortcuts import render
from .models import Product


def home(request):
    """Главная страница"""
    latest_products = Product.objects.all().order_by('-created_at')[:5]

    # Для допзадания: вывод в консоль
    print("Последние 5 продуктов:")
    for product in latest_products:
        print(f"  - {product.name} ({product.created_at})")

    context = {
        'latest_products': latest_products,
    }
    return render(request, 'catalog/home.html', context)


def contacts(request):
    """Страница контактов"""
    from .models import Contact
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
    all_contacts = Contact.objects.all() if hasattr(__import__('catalog.models'), 'Contact') else []

    return render(request, 'catalog/contacts.html', {
        'success_message': success_message,
        'contacts': all_contacts
    })