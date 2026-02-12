import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Загружает данные каталога из JSON файла (фикстуры)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="catalog/fixtures/catalog_data.json",
            help="Путь к JSON файлу с данными"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            default=True,
            help="Очистить базу перед загрузкой"
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        clear_db = options["clear"]
        
        self.stdout.write(self.style.SUCCESS(
            f"Начало загрузки каталога из файла: {file_path}"
        ))
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(
                f"Файл {file_path} не найден!"
            ))
            return
        
        try:
            # Используем utf-8-sig для автоматического удаления BOM если есть
            with open(file_path, "r", encoding="utf-8-sig") as file:
                data = json.load(file)
            
            self.stdout.write(f"Загружено {len(data)} записей из файла")
            
            if clear_db:
                self.stdout.write("Очистка базы данных...")
                Product.objects.all().delete()
                Category.objects.all().delete()
                self.stdout.write("База данных очищена")
            
            with transaction.atomic():
                categories_map = {}
                products_count = 0
                categories_count = 0
                
                # Создаем категории
                for item in data:
                    if item["model"] == "catalog.category":
                        category = Category.objects.create(
                            name=item["fields"]["name"],
                            description=item["fields"].get("description", "")
                        )
                        categories_map[item["pk"]] = category
                        categories_count += 1
                        self.stdout.write(f"Создана категория: {category.name}")
                
                # Создаем продукты
                for item in data:
                    if item["model"] == "catalog.product":
                        category_id = item["fields"]["category"]
                        category = categories_map.get(category_id)
                        
                        if category:
                            product = Product.objects.create(
                                name=item["fields"]["name"],
                                description=item["fields"].get("description", ""),
                                price=item["fields"]["price"],
                                category=category,
                                image=item["fields"].get("image", "")
                            )
                            products_count += 1
                            self.stdout.write(f"Создан продукт: {product.name}")
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"Категория {category_id} не найдена для продукта {item['fields']['name']}"
                            ))
                
                self.stdout.write(self.style.SUCCESS(
                    f"Загрузка завершена! Создано: {categories_count} категорий, {products_count} продуктов"
                ))
                
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Ошибка JSON: {e}"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Отсутствует поле: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
            raise
