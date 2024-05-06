# Generated by Django 5.0.3 on 2024-05-01 15:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artwork', '0002_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='title',
            field=models.TextField(default='Untitled Note'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='artwork_images/')),
                ('filename', models.CharField(max_length=100)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='artwork.artwork')),
            ],
        ),
    ]
