# Generated by Django 4.0.3 on 2022-06-04 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0003_teacherdata_collegeid_alter_teacherdata_firstname'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherdata',
            name='deviceid',
            field=models.CharField(default='Null', max_length=50),
            preserve_default=False,
        ),
    ]
