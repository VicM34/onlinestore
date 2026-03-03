from django.views.generic import ListView, DetailView, TemplateView
from .models import Product


class HomeListView(ListView):
    """Главная страница со списком товаров"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для допзадания: последние 5 продуктов
        context['latest_products'] = Product.objects.all().order_by('-created_at')[:5]
        return context

    def render_to_response(self, context, **response_kwargs):
        # Вывод в консоль для допзадания
        latest_products = context.get('latest_products', [])
        print("Последние 5 продуктов:")
        for product in latest_products:
            print(f"  - {product.name} ({product.created_at})")
        return super().render_to_response(context, **response_kwargs)


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ContactsView(TemplateView):
    """Страница контактов"""
    template_name = 'catalog/contacts.html'

    def post(self, request, *args, **kwargs):
        from .models import Contact

        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Сохраняем в базу данных
        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        context = self.get_context_data(**kwargs)
        context['success_message'] = "Спасибо! Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время."
        context['contacts'] = Contact.objects.all().order_by('-created_at')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Contact
        context['contacts'] = Contact.objects.all().order_by('-created_at')
        return context