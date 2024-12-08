# Generated by Django 5.1.3 on 2024-12-08 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0009_productreview_silenced_alter_productreview_rating"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"verbose_name": "Category", "verbose_name_plural": "Categories"},
        ),
        migrations.AlterField(
            model_name="product",
            name="name",
            field=models.CharField(max_length=35, unique=True),
        ),
        migrations.AlterField(
            model_name="productvariant",
            name="size",
            field=models.CharField(max_length=10),
        ),
    ]
