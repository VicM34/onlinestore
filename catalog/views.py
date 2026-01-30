from django.shortcuts import render


def home(request):
    """Контроллер для главной страницы"""
    return render(request, 'catalog/home.html')


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