from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from .models import Product, Category
from .forms import ProductForm
from .services import get_products_by_category, get_all_categories_with_products_count


class HomeListView(ListView):
    """Главная страница со списком товаров (доступна всем)"""
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'products'
    paginate_by = 12  # Пагинация для главной страницы

    def get_queryset(self):
        # Низкоуровневое кеширование для списка продуктов
        cache_key = 'home_products'
        products = cache.get(cache_key)

        if products is None:
            products = Product.objects.filter(
                is_published=True
            ).select_related('category', 'owner').order_by('-created_at')
            cache.set(cache_key, products, 60 * 5)  # Кешируем на 5 минут

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Кеширование для последних 5 продуктов
        latest_key = 'latest_products'
        latest_products = cache.get(latest_key)

        if latest_products is None:
            latest_products = Product.objects.filter(is_published=True).order_by('-created_at')[:5]
            cache.set(latest_key, latest_products, 60 * 5)

        context['latest_products'] = latest_products
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара с кешированием"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    @method_decorator(cache_page(60 * 15))  # Кешировать на 15 минут
    @method_decorator(vary_on_headers('Cookie', 'Authorization'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        # Используем низкоуровневое кеширование для объекта
        pk = self.kwargs.get('pk')
        cache_key = f'product_{pk}'
        product = cache.get(cache_key)

        if product is None:
            product = super().get_object(queryset)
            cache.set(cache_key, product, 60 * 15)  # Кешируем на 15 минут
            # Увеличиваем счетчик просмотров
            product.views_count += 1
            product.save()
            # Обновляем кеш с новым счетчиком
            cache.set(cache_key, product, 60 * 15)

        return product

    def get_queryset(self):
        # Показываем только опубликованные товары для всех
        return Product.objects.filter(is_published=True).order_by('-created_at')


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание продукта (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')
    login_url = 'users:login'

    def form_valid(self, form):
        # Автоматически назначаем владельца
        form.instance.owner = self.request.user
        messages.success(self.request, 'Продукт успешно создан!')

        # Очищаем кеш после создания продукта
        cache.delete('home_products')
        cache.delete('latest_products')

        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    login_url = 'users:login'
    raise_exception = True

    def test_func(self):
        """Проверка прав на редактирование"""
        product = self.get_object()
        user = self.request.user

        # Редактировать может владелец или модератор (с правом can_unpublish_product)
        return user == product.owner or user.has_perm('catalog.can_unpublish_product')

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно обновлен!')

        # Очищаем кеш после обновления
        cache.delete(f'product_{self.object.pk}')
        cache.delete('home_products')
        cache.delete('latest_products')

        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    login_url = 'users:login'
    raise_exception = True

    def test_func(self):
        """Проверка прав на удаление"""
        product = self.get_object()
        user = self.request.user

        # Удалять может владелец или модератор (с правом can_delete_any_product)
        return user == product.owner or user.has_perm('catalog.can_delete_any_product')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Продукт успешно удален!')

        cache.delete(f'product_{self.get_object().pk}')
        cache.delete('home_products')
        cache.delete('latest_products')

        return super().delete(request, *args, **kwargs)


class ContactsView(TemplateView):
    """Страница контактов (доступна всем)"""
    template_name = 'catalog/contacts.html'

    def post(self, request, *args, **kwargs):
        from .models import Contact

        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

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


class CategoryProductsView(ListView):
    """Список продуктов в выбранной категории"""
    model = Product
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return get_products_by_category(category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        context['category'] = Category.objects.get(id=category_id)
        context['categories'] = get_all_categories_with_products_count()
        return context