from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ejercicios', '0002_add_progreso_estudiante'),
    ]

    operations = [
        migrations.AddField(
            model_name='ejercicio',
            name='lenguaje',
            field=models.CharField(
                choices=[('cpp', 'C++'), ('python', 'Python')],
                default='cpp',
                max_length=10,
                verbose_name='Lenguaje del código',
            ),
        ),
    ]
