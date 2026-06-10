from django.db import migrations

CONTENIDO = """## Tema del problema

Sistema básico de control de estudiantes y calificaciones.

## Enunciado

Desarrollar un programa en **C++** y **Java** que permita registrar información de
estudiantes de la asignatura Algoritmos y Lógica de Programación, aplicando
programación orientada a objetos mediante clases, objetos y métodos.

Cada estudiante debe tener: cédula, nombre, apellido, nota 1, nota 2, nota 3,
promedio y estado (Aprobado / Reprobado).

## Requerimientos

Crear una clase `Estudiante`:

- En C++: `class Estudiante`
- En Java: `public class Estudiante`

La clase debe contener:

- Atributos privados
- Constructor
- Métodos get y set
- Método para calcular el promedio
- Método para determinar si aprueba o reprueba
- Método para mostrar la información del estudiante

## Funcionalidades mínimas

1. Registrar mínimo 5 estudiantes
2. Ingresar las 3 notas de cada estudiante
3. Calcular automáticamente el promedio
4. Mostrar el listado completo de estudiantes
5. Mostrar cuántos estudiantes aprobaron
6. Mostrar cuántos estudiantes reprobaron
7. Validar que las notas estén entre 0 y 10
8. Comentar correctamente el código

## Condición de aprobación

Un estudiante aprueba si su promedio es mayor o igual a **7.00**.

## Estructura sugerida del repositorio

    APE04-Clases-Objetos-Metodos/
    |-- Cpp/
    |   |-- main.cpp
    |   +-- README.md
    |-- Java/
    |   |-- Main.java
    |   |-- Estudiante.java
    |   +-- README.md
    |-- capturas/
    +-- README.md

## Evidencia obligatoria

- Código fuente en C++ y Java
- Capturas de ejecución y de las clases/métodos
- README con la explicación del proyecto
- Captura de los commits en GitHub

## Entregable final (Moodle)

- Enlace del repositorio GitHub
- Archivo PDF con todas las capturas (formato Guías APE)
"""


def crear_ape04(apps, schema_editor):
    Guia = apps.get_model('guias', 'Guia')
    Guia.objects.update_or_create(
        slug='ape-04-clases-objetos-metodos',
        defaults=dict(
            codigo='SW-AyLP-APE-04',
            titulo='Clases, Objetos y Métodos',
            resumen='POO en C++ y Java: sistema de control de estudiantes y calificaciones.',
            contenido=CONTENIDO,
            repo_url='',
            pdf='guias/ape-04.pdf',
            orden=4,
            publicada=True,
        ),
    )


def borrar_ape04(apps, schema_editor):
    Guia = apps.get_model('guias', 'Guia')
    Guia.objects.filter(slug='ape-04-clases-objetos-metodos').delete()


class Migration(migrations.Migration):
    dependencies = [('guias', '0001_initial')]
    operations = [migrations.RunPython(crear_ape04, borrar_ape04)]
