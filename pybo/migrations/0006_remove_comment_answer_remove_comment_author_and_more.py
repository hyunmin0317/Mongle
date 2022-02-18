# Generated by Django 4.0.1 on 2022-02-15 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0005_question_agency_question_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='question',
        ),
        migrations.RemoveField(
            model_name='question',
            name='author',
        ),
        migrations.RemoveField(
            model_name='question',
            name='voter',
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
    ]