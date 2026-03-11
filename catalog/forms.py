from django import forms
from .models import Product

# Список запрещенных слов (в нижнем регистре для проверки)
FORBIDDEN_WORDS = [
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
]


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продуктов"""

    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'category', 'price']
        labels = {
            'name': 'Название продукта',
            'description': 'Описание',
            'image': 'Изображение',
            'category': 'Категория',
            'price': 'Цена (руб.)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название продукта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание',
                'rows': 4
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        help_texts = {
            'price': 'Цена должна быть положительным числом',
        }

    def __init__(self, *args, **kwargs):
        """Добавляем стилизацию Bootstrap ко всем полям"""
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Добавляем класс form-control
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

            # Добавляем placeholder для полей, где его нет
            if not field.widget.attrs.get('placeholder') and field_name != 'category':
                field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'

    def clean_name(self):
        """Валидация названия продукта на запрещенные слова"""
        name = self.cleaned_data.get('name')
        if name:
            name_lower = name.lower()
            for word in FORBIDDEN_WORDS:
                if word in name_lower:
                    raise forms.ValidationError(
                        f'Название продукта не может содержать слово "{word}"'
                    )
        return name

    def clean_description(self):
        """Валидация описания продукта на запрещенные слова"""
        description = self.cleaned_data.get('description')
        if description:
            description_lower = description.lower()
            for word in FORBIDDEN_WORDS:
                if word in description_lower:
                    raise forms.ValidationError(
                        f'Описание продукта не может содержать слово "{word}"'
                    )
        return description

    def clean_price(self):
        """Валидация цены (не может быть отрицательной)"""
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise forms.ValidationError('Цена не может быть отрицательной')
            if price == 0:
                raise forms.ValidationError('Цена не может быть равной нулю')
        return price

    def clean_image(self):
        """Валидация изображения (дополнительное задание)"""
        image = self.cleaned_data.get('image')
        if image:
            # Проверка размера файла (не более 5 МБ)
            if image.size > 5 * 1024 * 1024:  # 5 MB
                raise forms.ValidationError(
                    'Размер изображения не должен превышать 5 МБ. '
                    f'Текущий размер: {image.size / (1024 * 1024):.1f} МБ'
                )

            # Проверка формата файла
            valid_formats = ['.jpg', '.jpeg', '.png']
            if not any(image.name.lower().endswith(fmt) for fmt in valid_formats):
                raise forms.ValidationError(
                    'Поддерживаются только форматы JPEG и PNG. '
                    f'Загружен файл: {image.name}'
                )

        return image