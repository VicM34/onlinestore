from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создание групп модераторов и контент-менеджеров'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем создание групп...'))

        product_content_type = ContentType.objects.get_for_model(Product)

        # Получаем нужные разрешения
        permissions = Permission.objects.filter(
            content_type=product_content_type,
            codename__in=['can_unpublish_product', 'can_delete_any_product']
        )

        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')
        moderator_group.permissions.set(permissions)

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модератор продуктов" создана'))
        else:
            self.stdout.write(self.style.SUCCESS('Группа "Модератор продуктов" уже существует'))

        content_manager_group, created = Group.objects.get_or_create(name='Контент-менеджер')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Контент-менеджер" создана'))
        else:
            self.stdout.write(self.style.SUCCESS('Группа "Контент-менеджер" уже существует'))

        self.stdout.write(self.style.SUCCESS('Все группы успешно созданы!'))