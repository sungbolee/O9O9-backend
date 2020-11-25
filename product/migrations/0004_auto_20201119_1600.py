# Generated by Django 3.1.2 on 2020-11-19 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        ('product', '0003_auto_20201119_1158'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='essencial',
            new_name='essential',
        ),
        migrations.RemoveField(
            model_name='product',
            name='buy_count',
        ),
        migrations.AddField(
            model_name='product',
            name='buy_count',
            field=models.ManyToManyField(null=True, related_name='buy_product', to='user.User'),
        ),
        migrations.AlterField(
            model_name='product',
            name='exchange',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='more_information',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='productgroup',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productgroup'),
        ),
        migrations.AlterField(
            model_name='product',
            name='seller_information',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='subsubcategy',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.subsubcategory'),
        ),
    ]