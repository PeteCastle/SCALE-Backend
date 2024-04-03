# Generated by Django 5.0.3 on 2024-03-29 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_areacoverage_images_system_systemfumigation_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='images',
            old_name='image',
            new_name='photo',
        ),
        migrations.AlterField(
            model_name='system',
            name='image',
            field=models.ImageField(upload_to='system'),
        ),
        migrations.AlterField(
            model_name='systemstatus',
            name='system',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='core.system'),
        ),
    ]