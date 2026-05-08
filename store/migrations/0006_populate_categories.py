from django.db import migrations
from django.utils.text import slugify

def populate_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    categories = [
        "Electronics",
        "Mobile Phones & Accessories",
        "Laptops & Computers",
        "Clothing & Fashion",
        "Men's Wear",
        "Women's Wear",
        "Books & Stationery",
        "Home & Kitchen",
        "Sports & Fitness",
        "Toys & Games",
        "Beauty & Personal Care",
        "Grocery & Food",
        "Furniture & Decor",
        "Automotive & Tools",
        "Health & Wellness",
    ]
    for name in categories:
        Category.objects.get_or_create(name=name, slug=slugify(name))

def reverse_populate_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    # Optional: Delete the created categories if needed
    categories = [
        "Electronics",
        "Mobile Phones & Accessories",
        "Laptops & Computers",
        "Clothing & Fashion",
        "Men's Wear",
        "Women's Wear",
        "Books & Stationery",
        "Home & Kitchen",
        "Sports & Fitness",
        "Toys & Games",
        "Beauty & Personal Care",
        "Grocery & Food",
        "Furniture & Decor",
        "Automotive & Tools",
        "Health & Wellness",
    ]
    Category.objects.filter(name__in=categories).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0005_orderitem_status'),
    ]

    operations = [
        migrations.RunPython(populate_categories, reverse_populate_categories),
    ]
