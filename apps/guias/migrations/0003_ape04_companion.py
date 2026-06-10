from django.db import migrations

CONTENIDO = """## Qué vas a practicar

Esta APE pone en práctica la **Programación Orientada a Objetos (POO)**:

- **Clase** y **objeto**: la clase `Estudiante` es el molde; cada estudiante registrado es un objeto.
- **Atributos** y **encapsulamiento**: los datos van *privados* y se acceden por métodos.
- **Constructor**: inicializa el objeto cuando lo creas.
- **Métodos get/set**: leer y modificar los atributos de forma controlada.
- **Métodos de comportamiento**: calcular el promedio y decidir aprobado/reprobado.

> ¿Necesitas repasar la teoría? Revisa la [sección de Teoría](/teoria/).

## El problema

Sistema básico de control de estudiantes y calificaciones, en **C++** y **Java**.
Cada estudiante tiene: cédula, nombre, apellido, 3 notas, promedio y estado
(Aprobado / Reprobado). **Aprueba** quien tenga promedio **mayor o igual a 7.00**.

Requisitos mínimos: registrar 5 estudiantes o más, ingresar 3 notas por estudiante,
calcular el promedio, listar a todos, contar aprobados y reprobados, validar que
cada nota esté entre 0 y 10, y comentar el código.

## Cómo desarrollarla, paso a paso

1. **Identifica los datos** de un estudiante: serán los **atributos privados**.
2. **Crea la clase `Estudiante`** con su **constructor** (cédula, nombre, apellido y las 3 notas).
3. Agrega los **get/set** de cada atributo.
4. Escribe `calcularPromedio()`: suma de las 3 notas dividida para 3.
5. Escribe `estaAprobado()`: verdadero si el promedio es **mayor o igual a 7.0**.
6. Escribe `mostrar()`: imprime los datos + promedio + estado.
7. En el **programa principal**: crea 5 objetos o más, recórrelos para **listar** y lleva **contadores** de aprobados y reprobados.
8. Antes de aceptar una nota, **valídala** (que esté entre 0 y 10).

## Diseño sugerido (pseudocódigo)

```text
clase Estudiante
    privado: cedula, nombre, apellido, nota1, nota2, nota3

    constructor(cedula, nombre, apellido, nota1, nota2, nota3)
    get / set de cada atributo

    calcularPromedio() -> (nota1 + nota2 + nota3) / 3
    estaAprobado()     -> calcularPromedio() >= 7.0
    mostrar()          -> imprime datos + promedio + "Aprobado / Reprobado"
```

> Esto es el **diseño**, no la solución: la implementación en C++ y Java es tu parte.

## Errores comunes a evitar

- Dejar los atributos **públicos** (rompe el encapsulamiento): deben ser privados.
- **No validar** que las notas estén entre 0 y 10.
- Usar `=` (asignación) en vez de `>=` al decidir si aprueba.
- Dividir con enteros y perder los decimales del promedio (usa `7.0`, no `7`).
- Olvidar **comentar** el código (la rúbrica lo pide).

## Checklist de entrega

- Código fuente en **C++** y en **Java**
- Capturas de la ejecución y de las clases/métodos
- **README** explicando el proyecto
- Mínimo **3 commits** en GitHub
- PDF con todas las capturas (formato Guías APE)
- Enlace del repositorio entregado en Moodle

## Recursos

- [Teoría](/teoria/) · [Ejercicios Resueltos](/ejercicios/resueltos/)
- El **PDF oficial** está en el botón de arriba.
"""

NUEVO_RESUMEN = 'Guía de estudio y desarrollo: POO en C++ y Java (clases, objetos y métodos).'


def enriquecer(apps, schema_editor):
    Guia = apps.get_model('guias', 'Guia')
    Guia.objects.filter(slug='ape-04-clases-objetos-metodos').update(
        contenido=CONTENIDO,
        resumen=NUEVO_RESUMEN,
    )


class Migration(migrations.Migration):
    dependencies = [('guias', '0002_seed_ape04')]
    operations = [migrations.RunPython(enriquecer, migrations.RunPython.noop)]
