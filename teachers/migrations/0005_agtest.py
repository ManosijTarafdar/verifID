# Generated by Django 4.0.3 on 2022-06-06 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0004_teacherdata_deviceid'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asg', models.ImageField(blank=True, null=True, upload_to='')),
            ],
        ),
    ]
