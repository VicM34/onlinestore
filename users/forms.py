from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'phone_number', 'country', 'avatar']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите страну'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Используем email как username
        if commit:
            user.save()
            # Отправка приветственного письма
            self.send_welcome_email(user)
        return user

    def send_welcome_email(self, user):
        """Отправка приветственного письма"""
        subject = 'Добро пожаловать в наш интернет-магазин!'
        message = f'''
        Здравствуйте!

        Спасибо за регистрацию в нашем интернет-магазине.
        Ваш email: {user.email}

        Теперь вы можете:
        - Просматривать товары
        - Добавлять новые товары
        - Редактировать существующие товары
        - Оставлять отзывы

        С уважением,
        Команда OnlineStore
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL or 'noreply@onlinestore.ru',
            [user.email],
            fail_silently=False,
        )


class UserLoginForm(AuthenticationForm):
    """Форма авторизации пользователя"""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем поле username, используем email
        self.fields['username'].label = 'Email'


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'country', 'avatar']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'  # Email нельзя изменить
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите страну'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'