# Implementación: Ejercicios Java

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar soporte para el lenguaje Java en la app `ejercicios` con 13 ejercicios nuevos (10 interactivos + 3 resueltos), siguiendo el mismo patrón usado para C++ y Python.

**Architecture:** Extender el campo `LENGUAJES` del modelo `Ejercicio` con `'java'`, generar migración, actualizar 4 plantillas y la vista de resueltos para soportar el nuevo lenguaje, y cargar los ejercicios al fixture `apps/ejercicios/fixtures/datos_iniciales.json` con pks 27–39.

**Tech Stack:** Django 5.x, Python 3.13, SQLite (dev), templates Django, Prism para syntax highlighting.

**Spec:** [docs/superpowers/specs/2026-05-27-ejercicios-java-design.md](../specs/2026-05-27-ejercicios-java-design.md)

---

## Archivos a tocar

| Archivo | Acción |
|---------|--------|
| `apps/ejercicios/models.py` | Modificar `LENGUAJES` (línea 47) |
| `apps/ejercicios/migrations/0004_add_java_to_lenguaje.py` | Crear (autogenerado) |
| `apps/ejercicios/views.py` | Modificar `ejercicios_resueltos` (líneas 23-33) |
| `templates/ejercicios/interactivo.html` | Modificar (líneas 23-43, 57) |
| `templates/ejercicios/resuelto.html` | Modificar (líneas 54-66) |
| `templates/ejercicios/lista_interactivos.html` | Modificar (líneas 17-27, 53-57) |
| `templates/ejercicios/lista_resueltos.html` | Modificar (líneas 6, 10-15, 22-28) |
| `fixtures/datos_iniciales.json` | Agregar 26 objetos (13 ejercicios + 13 retroalimentaciones) |

**Nota:** El fixture está en `fixtures/datos_iniciales.json` en la **raíz del proyecto**, NO dentro de `apps/ejercicios/fixtures/`. Confirmado por inspección del repositorio actual.

---

## Task 1: Agregar 'java' al campo LENGUAJES y migrar

**Files:**
- Modify: `apps/ejercicios/models.py:47`
- Create: `apps/ejercicios/migrations/0004_add_java_to_lenguaje.py`

- [ ] **Step 1: Modificar el modelo `Ejercicio`**

En [apps/ejercicios/models.py](../../apps/ejercicios/models.py) línea 47, reemplazar:

```python
    LENGUAJES    = [('cpp', 'C++'), ('python', 'Python')]
```

con:

```python
    LENGUAJES    = [('cpp', 'C++'), ('python', 'Python'), ('java', 'Java')]
```

- [ ] **Step 2: Generar la migración**

Ejecutar:

```bash
python manage.py makemigrations ejercicios
```

Resultado esperado (similar):

```
Migrations for 'ejercicios':
  apps\ejercicios\migrations\0004_alter_ejercicio_lenguaje.py
    ~ Alter field lenguaje on ejercicio
```

Si Django nombra el archivo distinto (ej. `0004_alter_ejercicio_lenguaje.py`), está bien — no es necesario renombrarlo.

- [ ] **Step 3: Aplicar la migración**

```bash
python manage.py migrate ejercicios
```

Resultado esperado:

```
Operations to perform:
  Apply all migrations: ejercicios
Running migrations:
  Applying ejercicios.0004_alter_ejercicio_lenguaje... OK
```

- [ ] **Step 4: Verificar que no hay migraciones pendientes**

```bash
python manage.py makemigrations --check --dry-run
```

Resultado esperado: `No changes detected` y exit code 0.

- [ ] **Step 5: Commit**

```bash
git add apps/ejercicios/models.py apps/ejercicios/migrations/0004_*.py
git commit -m "feat(ejercicios): add Java to LENGUAJES choices"
```

---

## Task 2: Agregar filtro de lenguaje en vista de resueltos

**Files:**
- Modify: `apps/ejercicios/views.py:23-33`

- [ ] **Step 1: Modificar la función `ejercicios_resueltos`**

En [apps/ejercicios/views.py](../../apps/ejercicios/views.py) reemplazar las líneas 23-33:

```python
def ejercicios_resueltos(request):
    ejercicios = Ejercicio.objects.filter(categoria='resuelto', activo=True).select_related('tema')
    temas = Tema.objects.filter(ejercicios__categoria='resuelto').distinct()
    unidad_filtro = request.GET.get('unidad')
    if unidad_filtro:
        ejercicios = ejercicios.filter(tema__unidad=unidad_filtro)
    return render(request, 'ejercicios/lista_resueltos.html', {
        'ejercicios': ejercicios,
        'temas': temas,
        'unidad_filtro': unidad_filtro,
    })
```

con:

```python
def ejercicios_resueltos(request):
    ejercicios = Ejercicio.objects.filter(categoria='resuelto', activo=True).select_related('tema')
    temas = Tema.objects.filter(ejercicios__categoria='resuelto').distinct()
    lenguaje_filtro = request.GET.get('lenguaje')
    unidad_filtro   = request.GET.get('unidad')
    if lenguaje_filtro:
        ejercicios = ejercicios.filter(lenguaje=lenguaje_filtro)
    if unidad_filtro:
        ejercicios = ejercicios.filter(tema__unidad=unidad_filtro)
    return render(request, 'ejercicios/lista_resueltos.html', {
        'ejercicios': ejercicios,
        'temas': temas,
        'lenguaje_filtro': lenguaje_filtro,
        'unidad_filtro': unidad_filtro,
    })
```

- [ ] **Step 2: Verificar que Django check pasa**

```bash
python manage.py check
```

Resultado esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Commit**

```bash
git add apps/ejercicios/views.py
git commit -m "feat(ejercicios): add language filter to resueltos view"
```

---

## Task 3: Actualizar plantilla de detalle interactivo

**Files:**
- Modify: `templates/ejercicios/interactivo.html`

- [ ] **Step 1: Reemplazar el bloque de etiqueta del código (líneas 23-27)**

Reemplazar:

```django
      {% if ejercicio.lenguaje == 'python' %}
        <h3 class="section-title" style="font-size:1rem">★ Código Python — Estúdialo antes de responder</h3>
      {% else %}
        <h3 class="section-title" style="font-size:1rem">★ Código C++ — Estúdialo antes de responder</h3>
      {% endif %}
```

con:

```django
      {% if ejercicio.lenguaje == 'python' %}
        <h3 class="section-title" style="font-size:1rem">★ Código Python — Estúdialo antes de responder</h3>
      {% elif ejercicio.lenguaje == 'java' %}
        <h3 class="section-title" style="font-size:1rem">★ Código Java — Estúdialo antes de responder</h3>
      {% else %}
        <h3 class="section-title" style="font-size:1rem">★ Código C++ — Estúdialo antes de responder</h3>
      {% endif %}
```

- [ ] **Step 2: Reemplazar el bloque de lang-label y badge (líneas 35-41)**

Reemplazar:

```django
          {% if ejercicio.lenguaje == 'python' %}
            <span class="lang-label">referencia.py</span>
            <span class="badge-cpp">Python</span>
          {% else %}
            <span class="lang-label">referencia.cpp</span>
            <span class="badge-cpp">C++17</span>
          {% endif %}
```

con:

```django
          {% if ejercicio.lenguaje == 'python' %}
            <span class="lang-label">referencia.py</span>
            <span class="badge-cpp">Python</span>
          {% elif ejercicio.lenguaje == 'java' %}
            <span class="lang-label">referencia.java</span>
            <span class="badge-cpp">Java 11</span>
          {% else %}
            <span class="lang-label">referencia.cpp</span>
            <span class="badge-cpp">C++17</span>
          {% endif %}
```

- [ ] **Step 3: Reemplazar la clase de Prism en el `<code>` (línea 43)**

Reemplazar:

```django
        <pre><code class="language-{% if ejercicio.lenguaje == 'python' %}python{% else %}cpp{% endif %}">{{ codigo_cpp }}</code></pre>
```

con:

```django
        <pre><code class="language-{% if ejercicio.lenguaje == 'python' %}python{% elif ejercicio.lenguaje == 'java' %}java{% else %}cpp{% endif %}">{{ codigo_cpp }}</code></pre>
```

- [ ] **Step 4: Reemplazar el texto "Basándote en el código X" (línea 57)**

Reemplazar:

```django
            Basándote en el código {% if ejercicio.lenguaje == 'python' %}Python{% else %}C++{% endif %}:<br>
```

con:

```django
            Basándote en el código {% if ejercicio.lenguaje == 'python' %}Python{% elif ejercicio.lenguaje == 'java' %}Java{% else %}C++{% endif %}:<br>
```

- [ ] **Step 5: Verificar que la plantilla compila**

```bash
python manage.py check
```

Resultado esperado: `System check identified no issues (0 silenced).`

(Django no valida sintaxis de plantilla hasta que se renderiza — la verificación visual se hará en Task 8).

- [ ] **Step 6: Commit**

```bash
git add templates/ejercicios/interactivo.html
git commit -m "feat(templates): add Java branch to interactivo template"
```

---

## Task 4: Actualizar plantilla de detalle resuelto

**Files:**
- Modify: `templates/ejercicios/resuelto.html`

La plantilla actual está hardcoded a C++. Hay que convertirla a `if/elif/else` para soportar los 3 lenguajes.

- [ ] **Step 1: Reemplazar el bloque del header del código (líneas 53-66)**

Reemplazar:

```django
    <!-- Código C++ educativo -->
    <div>
      <h3 class="section-title" style="font-size:1rem">Código C++ — Solución</h3>
      <div class="bloque-cpp">
        <div class="bloque-cpp-header">
          <div class="dots">
            <div class="dot dot-rojo"></div>
            <div class="dot dot-amarillo"></div>
            <div class="dot dot-verde"></div>
          </div>
          <span class="lang-label">{{ ejercicio.titulo|truncatechars:40 }}.cpp</span>
          <span class="badge-cpp">C++17</span>
        </div>
        <pre><code class="language-cpp">{{ codigo_cpp }}</code></pre>
      </div>
```

con:

```django
    <!-- Código educativo -->
    <div>
      <h3 class="section-title" style="font-size:1rem">
        {% if ejercicio.lenguaje == 'python' %}Código Python — Solución
        {% elif ejercicio.lenguaje == 'java' %}Código Java — Solución
        {% else %}Código C++ — Solución{% endif %}
      </h3>
      <div class="bloque-cpp">
        <div class="bloque-cpp-header">
          <div class="dots">
            <div class="dot dot-rojo"></div>
            <div class="dot dot-amarillo"></div>
            <div class="dot dot-verde"></div>
          </div>
          {% if ejercicio.lenguaje == 'python' %}
            <span class="lang-label">{{ ejercicio.titulo|truncatechars:40 }}.py</span>
            <span class="badge-cpp">Python</span>
          {% elif ejercicio.lenguaje == 'java' %}
            <span class="lang-label">{{ ejercicio.titulo|truncatechars:40 }}.java</span>
            <span class="badge-cpp">Java 11</span>
          {% else %}
            <span class="lang-label">{{ ejercicio.titulo|truncatechars:40 }}.cpp</span>
            <span class="badge-cpp">C++17</span>
          {% endif %}
        </div>
        <pre><code class="language-{% if ejercicio.lenguaje == 'python' %}python{% elif ejercicio.lenguaje == 'java' %}java{% else %}cpp{% endif %}">{{ codigo_cpp }}</code></pre>
      </div>
```

- [ ] **Step 2: Verificar Django check**

```bash
python manage.py check
```

Resultado esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Commit**

```bash
git add templates/ejercicios/resuelto.html
git commit -m "feat(templates): support Python/Java in resuelto detail template"
```

---

## Task 5: Agregar filtro Java en lista de interactivos

**Files:**
- Modify: `templates/ejercicios/lista_interactivos.html`

- [ ] **Step 1: Agregar botón Java al filtro (después de la línea 26)**

Reemplazar:

```django
      <a href="?lenguaje=python{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
         class="btn btn-sm {% if lenguaje_filtro == 'python' %}btn-primary{% else %}btn-outline{% endif %}"
         style="border-color:#3572A5;{% if lenguaje_filtro == 'python' %}background:#3572A5;color:#fff;{% endif %}">🐍 Python</a>
    </div>
```

con:

```django
      <a href="?lenguaje=python{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
         class="btn btn-sm {% if lenguaje_filtro == 'python' %}btn-primary{% else %}btn-outline{% endif %}"
         style="border-color:#3572A5;{% if lenguaje_filtro == 'python' %}background:#3572A5;color:#fff;{% endif %}">🐍 Python</a>
      <a href="?lenguaje=java{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
         class="btn btn-sm {% if lenguaje_filtro == 'java' %}btn-primary{% else %}btn-outline{% endif %}"
         style="border-color:#b07219;{% if lenguaje_filtro == 'java' %}background:#b07219;color:#fff;{% endif %}">☕ Java</a>
    </div>
```

- [ ] **Step 2: Agregar chip Java en la tarjeta del ejercicio (líneas 53-57)**

Reemplazar:

```django
            {% if ej.lenguaje == 'python' %}
              <span class="chip" style="background:#3572A5;color:#fff">🐍 Python</span>
            {% else %}
              <span class="chip" style="background:#00599C;color:#fff">C++</span>
            {% endif %}
```

con:

```django
            {% if ej.lenguaje == 'python' %}
              <span class="chip" style="background:#3572A5;color:#fff">🐍 Python</span>
            {% elif ej.lenguaje == 'java' %}
              <span class="chip" style="background:#b07219;color:#fff">☕ Java</span>
            {% else %}
              <span class="chip" style="background:#00599C;color:#fff">C++</span>
            {% endif %}
```

- [ ] **Step 3: Verificar Django check**

```bash
python manage.py check
```

Resultado esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 4: Commit**

```bash
git add templates/ejercicios/lista_interactivos.html
git commit -m "feat(templates): add Java filter and chip to interactivos list"
```

---

## Task 6: Agregar filtro Java en lista de resueltos

**Files:**
- Modify: `templates/ejercicios/lista_resueltos.html`

Esta plantilla no tiene filtro de lenguaje aún. Hay que agregarlo.

- [ ] **Step 1: Reemplazar título y subtítulo (líneas 6-7)**

Reemplazar:

```django
  <h1 class="section-title">💡 Ejercicios Resueltos — Código C++</h1>
  <p class="text-suave mb-3">Lee y analiza cada problema resuelto paso a paso con código C++ comentado.</p>
```

con:

```django
  <h1 class="section-title">💡 Ejercicios Resueltos — Código paso a paso</h1>
  <p class="text-suave mb-3">Lee y analiza cada problema resuelto paso a paso con código comentado en C++, Python o Java.</p>
```

- [ ] **Step 2: Reemplazar el bloque de filtros (líneas 9-15)**

Reemplazar:

```django
  <!-- Filtro por unidad -->
  <div class="flex-gap mb-3">
    <a href="{% url 'ejercicios_resueltos' %}" class="btn btn-sm {% if not unidad_filtro %}btn-primary{% else %}btn-outline{% endif %}">Todos</a>
    {% for i in "1234" %}
      <a href="?unidad={{ i }}" class="btn btn-sm {% if unidad_filtro == i %}btn-primary{% else %}btn-outline{% endif %}">U{{ i }}</a>
    {% endfor %}
  </div>
```

con:

```django
  <!-- Filtros -->
  <div style="display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem;align-items:center">
    <!-- Filtro por lenguaje -->
    <div class="flex-gap" style="gap:.4rem">
      <a href="?{% if unidad_filtro %}unidad={{ unidad_filtro }}&{% endif %}"
         class="btn btn-sm {% if not lenguaje_filtro %}btn-primary{% else %}btn-outline{% endif %}">Todos</a>
      <a href="?lenguaje=cpp{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
         class="btn btn-sm {% if lenguaje_filtro == 'cpp' %}btn-primary{% else %}btn-outline{% endif %}"
         style="border-color:#00599C;{% if lenguaje_filtro == 'cpp' %}background:#00599C;color:#fff;{% endif %}">C++</a>
      <a href="?lenguaje=python{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
         class="btn btn-sm {% if lenguaje_filtro == 'python' %}btn-primary{% else %}btn-outline{% endif %}"
         style="border-color:#3572A5;{% if lenguaje_filtro == 'python' %}background:#3572A5;color:#fff;{% endif %}">🐍 Python</a>
      <a href="?lenguaje=java{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
         class="btn btn-sm {% if lenguaje_filtro == 'java' %}btn-primary{% else %}btn-outline{% endif %}"
         style="border-color:#b07219;{% if lenguaje_filtro == 'java' %}background:#b07219;color:#fff;{% endif %}">☕ Java</a>
    </div>

    <span style="color:var(--texto-suave);font-size:.85rem;padding:0 .25rem">|</span>

    <!-- Filtro por unidad -->
    <div class="flex-gap" style="gap:.4rem">
      {% for i in "1234" %}
        <a href="?{% if lenguaje_filtro %}lenguaje={{ lenguaje_filtro }}&{% endif %}unidad={{ i }}"
           class="btn btn-sm {% if unidad_filtro == i %}btn-primary{% else %}btn-outline{% endif %}">U{{ i }}</a>
      {% endfor %}
      {% if unidad_filtro %}
        <a href="?{% if lenguaje_filtro %}lenguaje={{ lenguaje_filtro }}{% endif %}"
           class="btn btn-sm btn-outline">✕ Unidad</a>
      {% endif %}
    </div>
  </div>
```

- [ ] **Step 3: Reemplazar el bloque de metadata en la tarjeta (líneas 22-28)**

Reemplazar:

```django
          <div class="meta">
            <span class="chip chip-resuelto">📘 Resuelto</span>
            <span class="chip chip-{{ ej.dificultad }}">{{ ej.get_dificultad_display }}</span>
            <span class="chip chip-unidad">U{{ ej.tema.unidad }}</span>
          </div>
          <p style="font-size:.88rem;color:var(--texto-suave)">{{ ej.enunciado|truncatechars:110 }}</p>
          <span class="btn btn-primary btn-sm" style="margin-top:.25rem">Ver código C++ →</span>
```

con:

```django
          <div class="meta">
            <span class="chip chip-resuelto">📘 Resuelto</span>
            <span class="chip chip-{{ ej.dificultad }}">{{ ej.get_dificultad_display }}</span>
            <span class="chip chip-unidad">U{{ ej.tema.unidad }}</span>
            {% if ej.lenguaje == 'python' %}
              <span class="chip" style="background:#3572A5;color:#fff">🐍 Python</span>
            {% elif ej.lenguaje == 'java' %}
              <span class="chip" style="background:#b07219;color:#fff">☕ Java</span>
            {% else %}
              <span class="chip" style="background:#00599C;color:#fff">C++</span>
            {% endif %}
          </div>
          <p style="font-size:.88rem;color:var(--texto-suave)">{{ ej.enunciado|truncatechars:110 }}</p>
          <span class="btn btn-primary btn-sm" style="margin-top:.25rem">Ver solución →</span>
```

- [ ] **Step 4: Verificar Django check**

```bash
python manage.py check
```

Resultado esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Commit**

```bash
git add templates/ejercicios/lista_resueltos.html
git commit -m "feat(templates): add language filter and chip to resueltos list"
```

---

## Task 7: Agregar ejercicios interactivos básicos en Java (E1–E4)

**Files:**
- Modify: `fixtures/datos_iniciales.json`

Agregar al array principal del JSON, **antes del corchete final `]`** y después del último objeto existente (pk=26 ejercicio). Recuerda agregar **una coma** después del objeto anterior si todavía no la tiene.

- [ ] **Step 1: Agregar ejercicio pk=27 (Saludo con Scanner)**

Agregar después del último objeto del JSON (antes del `]` final):

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 27,
    "fields": {
      "titulo": "Saludo con Scanner — Java",
      "enunciado": "El programa lee un nombre desde teclado con Scanner y lo saluda. Si el usuario ingresa 'Ana', ¿qué texto exacto imprime el programa?",
      "categoria": "interactivo",
      "dificultad": "basico",
      "tema": 1,
      "orden": 30,
      "activo": true,
      "lenguaje": "java",
      "entrada": "nombre : String (leído por Scanner)",
      "proceso": "Concatenar 'Hola, ' + nombre + '!'",
      "salida": "saludo : String",
      "pseudocodigo": "INICIO\n  LEER nombre\n  ESCRIBIR 'Hola, ' + nombre + '!'\nFIN",
      "codigo_cpp": "import java.util.Scanner;\n\npublic class Saludo {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n        // --- ENTRADA ---\n        System.out.print(\"Ingresa tu nombre: \");\n        String nombre = sc.nextLine();\n\n        // --- PROCESO + SALIDA ---\n        System.out.println(\"Hola, \" + nombre + \"!\");\n\n        sc.close();\n    }\n}",
      "solucion_esperada": "Hola, Ana!",
      "tipo_respuesta": "texto"
    }
  }
```

- [ ] **Step 2: Agregar ejercicio pk=28 (Suma de dos enteros)**

Agregar a continuación (con coma `,` separando los objetos):

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 28,
    "fields": {
      "titulo": "Suma de dos enteros — Java",
      "enunciado": "El código Java lee dos enteros con Scanner y muestra su suma. Si a=12 y b=8, ¿qué valor imprime suma?",
      "categoria": "interactivo",
      "dificultad": "basico",
      "tema": 2,
      "orden": 30,
      "activo": true,
      "lenguaje": "java",
      "entrada": "a=12, b=8 (int)",
      "proceso": "suma = a + b",
      "salida": "suma (int)",
      "pseudocodigo": "INICIO\n  LEER a, b\n  suma <- a + b\n  ESCRIBIR suma\nFIN",
      "codigo_cpp": "import java.util.Scanner;\n\npublic class Suma {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n        System.out.print(\"Primer número: \");\n        int a = sc.nextInt();\n        System.out.print(\"Segundo número: \");\n        int b = sc.nextInt();\n\n        int suma = a + b;\n        System.out.println(\"Suma: \" + suma);\n\n        // Para a=12, b=8 -> suma = ?\n\n        sc.close();\n    }\n}",
      "solucion_esperada": "20",
      "tipo_respuesta": "entero"
    }
  }
```

- [ ] **Step 3: Agregar ejercicio pk=29 (Promedio de tres notas)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 29,
    "fields": {
      "titulo": "Promedio de tres notas — Java",
      "enunciado": "El programa pide tres notas con Scanner y muestra el promedio. Si n1=8, n2=6, n3=7, ¿cuál es el promedio?",
      "categoria": "interactivo",
      "dificultad": "basico",
      "tema": 2,
      "orden": 31,
      "activo": true,
      "lenguaje": "java",
      "entrada": "n1, n2, n3 : double",
      "proceso": "prom = (n1 + n2 + n3) / 3.0",
      "salida": "prom : double",
      "pseudocodigo": "INICIO\n  LEER n1, n2, n3\n  prom <- (n1 + n2 + n3) / 3\n  ESCRIBIR prom\nFIN",
      "codigo_cpp": "import java.util.Scanner;\n\npublic class Promedio {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n        System.out.print(\"Nota 1: \"); double n1 = sc.nextDouble();\n        System.out.print(\"Nota 2: \"); double n2 = sc.nextDouble();\n        System.out.print(\"Nota 3: \"); double n3 = sc.nextDouble();\n\n        // Dividir entre 3.0 (double) preserva los decimales\n        double prom = (n1 + n2 + n3) / 3.0;\n        System.out.println(\"Promedio: \" + prom);\n\n        // n1=8, n2=6, n3=7 -> prom = ?\n\n        sc.close();\n    }\n}",
      "solucion_esperada": "7",
      "tipo_respuesta": "decimal"
    }
  }
```

- [ ] **Step 4: Agregar ejercicio pk=30 (Mayor de tres números)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 30,
    "fields": {
      "titulo": "Mayor de tres números — Java",
      "enunciado": "Analiza el código Java que encuentra el mayor de tres números usando if/else if. Si a=15, b=42, c=27, ¿qué valor imprime mayor?",
      "categoria": "interactivo",
      "dificultad": "basico",
      "tema": 2,
      "orden": 32,
      "activo": true,
      "lenguaje": "java",
      "entrada": "a=15, b=42, c=27 (int)",
      "proceso": "Comparar a, b, c con estructuras if/else if anidadas",
      "salida": "mayor (int)",
      "pseudocodigo": "INICIO\n  LEER a, b, c\n  SI a > b Y a > c ENTONCES\n    mayor <- a\n  SINO SI b > c ENTONCES\n    mayor <- b\n  SINO\n    mayor <- c\n  FIN SI\n  ESCRIBIR mayor\nFIN",
      "codigo_cpp": "import java.util.Scanner;\n\npublic class Mayor {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n\n        System.out.print(\"a: \"); int a = sc.nextInt();\n        System.out.print(\"b: \"); int b = sc.nextInt();\n        System.out.print(\"c: \"); int c = sc.nextInt();\n\n        int mayor;\n        if (a > b && a > c) {\n            mayor = a;\n        } else if (b > c) {\n            mayor = b;\n        } else {\n            mayor = c;\n        }\n\n        System.out.println(\"El mayor es: \" + mayor);\n\n        // a=15, b=42, c=27 -> mayor = ?\n\n        sc.close();\n    }\n}",
      "solucion_esperada": "42",
      "tipo_respuesta": "entero"
    }
  }
```

- [ ] **Step 5: Validar que el JSON sigue siendo válido**

```bash
python -c "import json; data = json.load(open('fixtures/datos_iniciales.json', encoding='utf-8')); print(f'Total objects: {len(data)}'); print(f'Java exercises so far: {sum(1 for o in data if o[\"model\"] == \"ejercicios.ejercicio\" and o[\"fields\"].get(\"lenguaje\") == \"java\")}')"
```

Resultado esperado:

```
Total objects: 49
Java exercises so far: 4
```

(49 = 4 temas + 26 ejercicios previos + 4 Java nuevos + 15 retros previas)

- [ ] **Step 6: Commit**

```bash
git add fixtures/datos_iniciales.json
git commit -m "feat(fixtures): add 4 basic Java interactive exercises (E1-E4)"
```

---

## Task 8: Agregar ejercicios interactivos medios y avanzados Java (E5–E10)

**Files:**
- Modify: `fixtures/datos_iniciales.json`

- [ ] **Step 1: Agregar ejercicio pk=31 (Factorial con while — medio)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 31,
    "fields": {
      "titulo": "Factorial con while — Java",
      "enunciado": "El código Java calcula el factorial de un número con un ciclo while. Si n=6, ¿qué valor imprime resultado?",
      "categoria": "interactivo",
      "dificultad": "medio",
      "tema": 2,
      "orden": 33,
      "activo": true,
      "lenguaje": "java",
      "entrada": "n = 6 (int)",
      "proceso": "Acumular resultado *= i para i de 1 a n",
      "salida": "resultado (long)",
      "pseudocodigo": "INICIO\n  LEER n\n  resultado <- 1\n  i <- 1\n  MIENTRAS i <= n HACER\n    resultado <- resultado * i\n    i <- i + 1\n  FIN MIENTRAS\n  ESCRIBIR resultado\nFIN",
      "codigo_cpp": "import java.util.Scanner;\n\npublic class Factorial {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        System.out.print(\"Ingresa n: \");\n        int n = sc.nextInt();\n\n        long resultado = 1;\n        int i = 1;\n        while (i <= n) {\n            resultado *= i;   // equivalente a resultado = resultado * i\n            i++;\n        }\n\n        System.out.println(\"factorial(\" + n + \") = \" + resultado);\n\n        // n=6: 1, 2, 6, 24, 120, ?\n\n        sc.close();\n    }\n}",
      "solucion_esperada": "720",
      "tipo_respuesta": "entero"
    }
  }
```

- [ ] **Step 2: Agregar ejercicio pk=32 (Fibonacci recursivo — avanzado)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 32,
    "fields": {
      "titulo": "Fibonacci recursivo — Java",
      "enunciado": "El método fib(n) calcula el n-ésimo término de la serie de Fibonacci con recursión. La serie es 0, 1, 1, 2, 3, 5, 8, 13, ... ¿Qué valor imprime fib(7)?",
      "categoria": "interactivo",
      "dificultad": "avanzado",
      "tema": 2,
      "orden": 34,
      "activo": true,
      "lenguaje": "java",
      "entrada": "n = 7 (int)",
      "proceso": "fib(n) = fib(n-1) + fib(n-2); casos base: fib(0)=0, fib(1)=1",
      "salida": "fib(n) (int)",
      "pseudocodigo": "FUNCION fib(n)\n  SI n <= 1 ENTONCES\n    RETORNAR n\n  SINO\n    RETORNAR fib(n-1) + fib(n-2)\n  FIN SI\nFIN FUNCION",
      "codigo_cpp": "public class Fibonacci {\n    // Función recursiva: fib(n) = fib(n-1) + fib(n-2)\n    public static int fib(int n) {\n        if (n <= 1) return n;       // casos base: fib(0)=0, fib(1)=1\n        return fib(n - 1) + fib(n - 2);\n    }\n\n    public static void main(String[] args) {\n        int n = 7;\n        System.out.println(\"fib(\" + n + \") = \" + fib(n));\n\n        // Serie: 0, 1, 1, 2, 3, 5, 8, 13, ...\n        // Índices: 0  1  2  3  4  5  6  7\n        // fib(7) = ?\n    }\n}",
      "solucion_esperada": "13",
      "tipo_respuesta": "entero"
    }
  }
```

- [ ] **Step 3: Agregar ejercicio pk=33 (Clase Estudiante — POO, medio)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 33,
    "fields": {
      "titulo": "Clase Estudiante (POO) — Java",
      "enunciado": "Analiza la clase Estudiante en Java. Si se crea new Estudiante(\"Luis\", 10, 8, 9) y se llama calcularPromedio(), ¿qué valor retorna el método?",
      "categoria": "interactivo",
      "dificultad": "medio",
      "tema": 3,
      "orden": 30,
      "activo": true,
      "lenguaje": "java",
      "entrada": "nombre='Luis', n1=10, n2=8, n3=9",
      "proceso": "promedio = (n1 + n2 + n3) / 3.0",
      "salida": "promedio (double)",
      "pseudocodigo": "CLASE Estudiante\n  ATRIBUTOS: nombre, nota1, nota2, nota3\n  METODO calcularPromedio()\n    RETORNAR (nota1 + nota2 + nota3) / 3.0\n  FIN METODO\nFIN CLASE",
      "codigo_cpp": "public class Estudiante {\n    private String nombre;\n    private double nota1, nota2, nota3;\n\n    // Constructor\n    public Estudiante(String nombre, double n1, double n2, double n3) {\n        this.nombre = nombre;\n        this.nota1  = n1;\n        this.nota2  = n2;\n        this.nota3  = n3;\n    }\n\n    // Método de cálculo\n    public double calcularPromedio() {\n        return (nota1 + nota2 + nota3) / 3.0;\n    }\n\n    public void mostrar() {\n        System.out.println(\"Estudiante: \" + nombre);\n        System.out.println(\"Promedio:   \" + calcularPromedio());\n    }\n\n    public static void main(String[] args) {\n        Estudiante est = new Estudiante(\"Luis\", 10, 8, 9);\n        est.mostrar();\n\n        // calcularPromedio() = (10 + 8 + 9) / 3.0 = ?\n    }\n}",
      "solucion_esperada": "9",
      "tipo_respuesta": "decimal"
    }
  }
```

- [ ] **Step 4: Agregar ejercicio pk=34 (Herencia Animal/Perro — avanzado)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 34,
    "fields": {
      "titulo": "Herencia y polimorfismo: Animal/Perro — Java",
      "enunciado": "Analiza la clase Animal y su subclase Perro. Si Animal a = new Perro() y se invoca a.hablar(), ¿qué texto exacto imprime el programa?",
      "categoria": "interactivo",
      "dificultad": "avanzado",
      "tema": 3,
      "orden": 31,
      "activo": true,
      "lenguaje": "java",
      "entrada": "Animal a = new Perro()",
      "proceso": "Polimorfismo: Java ejecuta el método de la subclase real (Perro), no el de la referencia (Animal)",
      "salida": "String impreso",
      "pseudocodigo": "CLASE Animal\n  METODO hablar()\n    RETORNAR 'sonido genérico'\n  FIN METODO\nFIN CLASE\n\nCLASE Perro HEREDA Animal\n  METODO hablar()  // sobreescribe\n    RETORNAR 'guau guau'\n  FIN METODO\nFIN CLASE",
      "codigo_cpp": "class Animal {\n    public String hablar() {\n        return \"sonido genérico\";\n    }\n}\n\nclass Perro extends Animal {\n    @Override\n    public String hablar() {       // sobreescribe el método del padre\n        return \"guau guau\";\n    }\n}\n\npublic class Herencia {\n    public static void main(String[] args) {\n        Animal a = new Perro();    // referencia Animal, objeto real Perro\n        System.out.println(a.hablar());\n\n        // Polimorfismo: Java decide el método según el OBJETO,\n        // no según la referencia. ¿Qué texto exacto se imprime?\n    }\n}",
      "solucion_esperada": "guau guau",
      "tipo_respuesta": "texto"
    }
  }
```

- [ ] **Step 5: Agregar ejercicio pk=35 (Suma de elementos de un arreglo — medio)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 35,
    "fields": {
      "titulo": "Suma de elementos de un arreglo — Java",
      "enunciado": "El código Java recorre un arreglo con for-each y acumula la suma. Si el arreglo es {4, 7, 2, 9, 3}, ¿qué valor imprime suma?",
      "categoria": "interactivo",
      "dificultad": "medio",
      "tema": 4,
      "orden": 30,
      "activo": true,
      "lenguaje": "java",
      "entrada": "numeros = {4, 7, 2, 9, 3} (int[])",
      "proceso": "Acumular suma += n para cada n del arreglo",
      "salida": "suma (int)",
      "pseudocodigo": "INICIO\n  numeros <- {4, 7, 2, 9, 3}\n  suma <- 0\n  PARA CADA n EN numeros HACER\n    suma <- suma + n\n  FIN PARA\n  ESCRIBIR suma\nFIN",
      "codigo_cpp": "public class SumaArreglo {\n    public static void main(String[] args) {\n        int[] numeros = {4, 7, 2, 9, 3};\n\n        int suma = 0;\n        // for-each (forEach) recorre todos los elementos del arreglo\n        for (int n : numeros) {\n            suma += n;\n        }\n\n        System.out.println(\"Suma: \" + suma);\n\n        // 4 + 7 + 2 + 9 + 3 = ?\n    }\n}",
      "solucion_esperada": "25",
      "tipo_respuesta": "entero"
    }
  }
```

- [ ] **Step 6: Agregar ejercicio pk=36 (Ordenamiento burbuja — avanzado)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 36,
    "fields": {
      "titulo": "Ordenamiento burbuja — Java",
      "enunciado": "El método ordenar() aplica el algoritmo burbuja al arreglo. Si el arreglo inicial es {7, 3, 9, 1, 5}, ¿qué valor tiene numeros[0] después de ordenarlo de menor a mayor?",
      "categoria": "interactivo",
      "dificultad": "avanzado",
      "tema": 4,
      "orden": 31,
      "activo": true,
      "lenguaje": "java",
      "entrada": "numeros = {7, 3, 9, 1, 5} (int[])",
      "proceso": "Burbuja: comparar pares adyacentes e intercambiar si están fuera de orden",
      "salida": "numeros[0] tras ordenar (int)",
      "pseudocodigo": "PARA i <- 0 HASTA n-2 HACER\n  PARA j <- 0 HASTA n-2-i HACER\n    SI v[j] > v[j+1] ENTONCES\n      INTERCAMBIAR v[j] y v[j+1]\n    FIN SI\n  FIN PARA\nFIN PARA",
      "codigo_cpp": "public class Burbuja {\n    public static void ordenar(int[] v) {\n        int n = v.length;\n        for (int i = 0; i < n - 1; i++) {\n            for (int j = 0; j < n - 1 - i; j++) {\n                if (v[j] > v[j + 1]) {\n                    // Intercambio\n                    int temp = v[j];\n                    v[j]     = v[j + 1];\n                    v[j + 1] = temp;\n                }\n            }\n        }\n    }\n\n    public static void main(String[] args) {\n        int[] numeros = {7, 3, 9, 1, 5};\n\n        ordenar(numeros);\n\n        // Después de ordenar: {1, 3, 5, 7, 9}\n        // ¿Qué valor tiene numeros[0]?\n        System.out.println(numeros[0]);\n    }\n}",
      "solucion_esperada": "1",
      "tipo_respuesta": "entero"
    }
  }
```

- [ ] **Step 7: Validar JSON**

```bash
python -c "import json; data = json.load(open('fixtures/datos_iniciales.json', encoding='utf-8')); print(f'Java exercises: {sum(1 for o in data if o[\"model\"] == \"ejercicios.ejercicio\" and o[\"fields\"].get(\"lenguaje\") == \"java\")}')"
```

Resultado esperado: `Java exercises: 10`

- [ ] **Step 8: Commit**

```bash
git add fixtures/datos_iniciales.json
git commit -m "feat(fixtures): add 6 medium/advanced Java interactive exercises (E5-E10)"
```

---

## Task 9: Agregar ejercicios resueltos Java (E11–E13)

**Files:**
- Modify: `fixtures/datos_iniciales.json`

- [ ] **Step 1: Agregar ejercicio pk=37 (Estructura básica de un programa Java — resuelto básico)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 37,
    "fields": {
      "titulo": "Estructura básica de un programa Java",
      "enunciado": "Aprende los elementos mínimos de un programa Java: clase pública, método main y la sentencia System.out.println. Incluye análisis IPO y código comentado paso a paso.",
      "categoria": "resuelto",
      "dificultad": "basico",
      "tema": 1,
      "orden": 40,
      "activo": true,
      "lenguaje": "java",
      "entrada": "(ninguna — el programa no lee del usuario)",
      "proceso": "Imprimir literal por consola con System.out.println",
      "salida": "Cadena literal 'Hola, mundo!'",
      "pseudocodigo": "INICIO\n  ESCRIBIR 'Hola, mundo!'\nFIN",
      "codigo_cpp": "// ╭───────────────────────────────────────╮\n// │  Estructura mínima de un programa Java │\n// ╰───────────────────────────────────────╯\n//\n// Todo programa Java requiere:\n//   1) Una clase pública con el mismo nombre del archivo (Hola.java)\n//   2) Un método main como punto de entrada\n//   3) Sentencias dentro del main para hacer algo\n\npublic class Hola {\n    // El método main es el punto de inicio del programa\n    public static void main(String[] args) {\n        // System.out.println imprime una línea en la consola\n        System.out.println(\"Hola, mundo!\");\n    }\n}",
      "solucion_esperada": "N/A",
      "tipo_respuesta": "texto"
    }
  }
```

- [ ] **Step 2: Agregar ejercicio pk=38 (POO en Java: clase con constructor y métodos — resuelto medio)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 38,
    "fields": {
      "titulo": "POO en Java: clase Persona con encapsulación",
      "enunciado": "Implementación completa de la clase Persona con atributos privados, constructor, getters/setters, validación en setter y método de negocio. Ejemplo canónico de encapsulación en Java.",
      "categoria": "resuelto",
      "dificultad": "medio",
      "tema": 3,
      "orden": 40,
      "activo": true,
      "lenguaje": "java",
      "entrada": "nombre : String, edad : int",
      "proceso": "Crear objeto, leer atributos con getters, evaluar esMayorDeEdad()",
      "salida": "Datos de la persona y si es mayor de edad",
      "pseudocodigo": "CLASE Persona\n  ATRIBUTOS PRIVADOS: nombre, edad\n  CONSTRUCTOR(nombre, edad)\n  METODO getNombre()\n  METODO getEdad()\n  METODO setEdad(edad) (valida edad >= 0)\n  METODO esMayorDeEdad()\n    RETORNAR edad >= 18\n  FIN METODO\nFIN CLASE",
      "codigo_cpp": "// ╭──────────────────────────────────────────╮\n// │  Encapsulación con clase Persona en Java │\n// ╰──────────────────────────────────────────╯\n\npublic class Persona {\n    // Atributos privados (encapsulación)\n    private String nombre;\n    private int edad;\n\n    // Constructor: recibe los datos iniciales del objeto\n    public Persona(String nombre, int edad) {\n        this.nombre = nombre;   // 'this' diferencia el atributo del parámetro\n        this.edad   = edad;\n    }\n\n    // Getters: permiten leer atributos privados\n    public String getNombre() { return nombre; }\n    public int    getEdad()   { return edad; }\n\n    // Setter: permite modificar la edad con validación\n    public void setEdad(int edad) {\n        if (edad >= 0) {        // protege el atributo de valores inválidos\n            this.edad = edad;\n        }\n    }\n\n    // Método de negocio\n    public boolean esMayorDeEdad() {\n        return edad >= 18;\n    }\n\n    // Punto de entrada del programa\n    public static void main(String[] args) {\n        Persona p = new Persona(\"María\", 21);\n\n        System.out.println(\"Nombre:    \" + p.getNombre());\n        System.out.println(\"Edad:      \" + p.getEdad());\n        System.out.println(\"¿Mayor?:   \" + p.esMayorDeEdad());\n    }\n}",
      "solucion_esperada": "N/A",
      "tipo_respuesta": "texto"
    }
  }
```

- [ ] **Step 3: Agregar ejercicio pk=39 (Búsqueda binaria con ArrayList — resuelto avanzado)**

```json
  ,
  {
    "model": "ejercicios.ejercicio",
    "pk": 39,
    "fields": {
      "titulo": "Búsqueda binaria con ArrayList — Java",
      "enunciado": "Algoritmo eficiente para buscar un elemento en una lista ordenada. Divide el rango a la mitad en cada paso, alcanzando complejidad O(log n).",
      "categoria": "resuelto",
      "dificultad": "avanzado",
      "tema": 4,
      "orden": 40,
      "activo": true,
      "lenguaje": "java",
      "entrada": "ArrayList<Integer> ordenado, int clave",
      "proceso": "Mantener inicio/fin; en cada iteración tomar el medio y descartar la mitad que no contiene la clave",
      "salida": "índice de la clave, o -1 si no existe",
      "pseudocodigo": "FUNCION buscar(lista, clave)\n  inicio <- 0\n  fin <- tamano(lista) - 1\n  MIENTRAS inicio <= fin HACER\n    medio <- (inicio + fin) / 2\n    SI lista[medio] = clave ENTONCES\n      RETORNAR medio\n    SINO SI lista[medio] < clave ENTONCES\n      inicio <- medio + 1\n    SINO\n      fin <- medio - 1\n    FIN SI\n  FIN MIENTRAS\n  RETORNAR -1\nFIN FUNCION",
      "codigo_cpp": "// ╭───────────────────────────────────────────────────╮\n// │  Búsqueda binaria sobre una lista ordenada (Java) │\n// ╰───────────────────────────────────────────────────╯\n//\n// Pre-condición: la lista DEBE estar ordenada de menor a mayor.\n// La búsqueda binaria divide el rango a la mitad en cada paso.\n// Complejidad: O(log n), mucho mejor que la lineal O(n).\n\nimport java.util.ArrayList;\nimport java.util.Arrays;\n\npublic class BusquedaBinaria {\n\n    // Retorna el índice del elemento o -1 si no existe\n    public static int buscar(ArrayList<Integer> lista, int clave) {\n        int inicio = 0;\n        int fin    = lista.size() - 1;\n\n        while (inicio <= fin) {\n            int medio = (inicio + fin) / 2;\n            int valor = lista.get(medio);\n\n            if (valor == clave) {\n                return medio;            // encontrado\n            } else if (valor < clave) {\n                inicio = medio + 1;      // buscar en la mitad superior\n            } else {\n                fin    = medio - 1;      // buscar en la mitad inferior\n            }\n        }\n        return -1;                       // no encontrado\n    }\n\n    public static void main(String[] args) {\n        ArrayList<Integer> datos = new ArrayList<>(\n            Arrays.asList(2, 5, 8, 12, 16, 23, 38, 56, 72, 91)\n        );\n\n        int clave = 23;\n        int pos   = buscar(datos, clave);\n\n        if (pos != -1) {\n            System.out.println(\"Encontrado en índice: \" + pos);\n        } else {\n            System.out.println(\"No encontrado.\");\n        }\n    }\n}",
      "solucion_esperada": "N/A",
      "tipo_respuesta": "texto"
    }
  }
```

- [ ] **Step 4: Validar JSON y conteos**

```bash
python -c "import json; data = json.load(open('fixtures/datos_iniciales.json', encoding='utf-8')); print(f'Java interactivos: {sum(1 for o in data if o[\"model\"] == \"ejercicios.ejercicio\" and o[\"fields\"].get(\"lenguaje\") == \"java\" and o[\"fields\"][\"categoria\"] == \"interactivo\")}'); print(f'Java resueltos: {sum(1 for o in data if o[\"model\"] == \"ejercicios.ejercicio\" and o[\"fields\"].get(\"lenguaje\") == \"java\" and o[\"fields\"][\"categoria\"] == \"resuelto\")}')"
```

Resultado esperado:

```
Java interactivos: 10
Java resueltos: 3
```

- [ ] **Step 5: Commit**

```bash
git add fixtures/datos_iniciales.json
git commit -m "feat(fixtures): add 3 Java resuelto exercises (E11-E13)"
```

---

## Task 10: Agregar retroalimentaciones para los 13 ejercicios Java

**Files:**
- Modify: `fixtures/datos_iniciales.json`

Las retroalimentaciones se crean solo para los **10 ejercicios interactivos** (pks 27-36). Los resueltos no requieren retroalimentación (no se evalúan).

Los pks de las retroalimentaciones nuevas son **19-28** (continuando desde la última pk=18 existente).

- [ ] **Step 1: Agregar las 10 retroalimentaciones**

Agregar después del último objeto del fixture (manteniendo la coma):

```json
  ,
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 19,
    "fields": {
      "ejercicio": 27,
      "mensaje_correcto": "¡Excelente! El programa concatena 'Hola, ' + nombre + '!' produciendo 'Hola, Ana!'.",
      "mensaje_error": "Recuerda que la respuesta debe coincidir exactamente: 'Hola, Ana!' con la coma, el espacio y el signo de admiración.",
      "recomendacion": "Repasa entrada por Scanner y concatenación de Strings en Java — Unidad 1."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 20,
    "fields": {
      "ejercicio": 28,
      "mensaje_correcto": "¡Bien hecho! 12 + 8 = 20. El operador + funciona con int como en cualquier lenguaje.",
      "mensaje_error": "Suma los dos valores ingresados: 12 + 8 = ?",
      "recomendacion": "Repasa variables int y operadores aritméticos en Java — Unidad 2."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 21,
    "fields": {
      "ejercicio": 29,
      "mensaje_correcto": "¡Excelente! (8 + 6 + 7) / 3.0 = 21 / 3.0 = 7.0. Al usar double y dividir entre 3.0 conservas decimales.",
      "mensaje_error": "Suma las tres notas (8+6+7=21) y divide entre 3. El resultado es 7.0.",
      "recomendacion": "Repasa el tipo double y la división con punto flotante en Java — Unidad 2."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 22,
    "fields": {
      "ejercicio": 30,
      "mensaje_correcto": "¡Correcto! b=42 es el mayor: 42 > 15 y 42 > 27.",
      "mensaje_error": "Compara a=15, b=42, c=27. ¿Cuál es el más grande de los tres?",
      "recomendacion": "Repasa estructuras condicionales if/else if anidadas en Java — Unidad 2."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 23,
    "fields": {
      "ejercicio": 31,
      "mensaje_correcto": "¡Perfecto! 6! = 1·2·3·4·5·6 = 720. El while multiplica resultado por i hasta i = n.",
      "mensaje_error": "Multiplica acumulativamente: 1·2=2, ·3=6, ·4=24, ·5=120, ·6=?",
      "recomendacion": "Practica ciclos while y acumuladores en Java — Unidad 2."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 24,
    "fields": {
      "ejercicio": 32,
      "mensaje_correcto": "¡Muy bien! fib(7) = fib(6) + fib(5) = 8 + 5 = 13. La serie es 0,1,1,2,3,5,8,13.",
      "mensaje_error": "Construye la serie: 0, 1, 1, 2, 3, 5, 8, 13. Los índices empiezan en 0, así que fib(7) es el octavo término.",
      "recomendacion": "Repasa recursividad, caso base y la serie de Fibonacci — Unidad 2."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 25,
    "fields": {
      "ejercicio": 33,
      "mensaje_correcto": "¡Correcto! calcularPromedio() retorna (10 + 8 + 9) / 3.0 = 27 / 3.0 = 9.0.",
      "mensaje_error": "El método suma las tres notas y divide entre 3.0. Con 10, 8 y 9: (10+8+9)/3.0 = ?",
      "recomendacion": "Repasa clases, constructor con 'this' y métodos en Java — Unidad 3."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 26,
    "fields": {
      "ejercicio": 34,
      "mensaje_correcto": "¡Muy bien! Aunque la referencia es Animal, el objeto real es Perro, así que se ejecuta hablar() de Perro. Eso es polimorfismo.",
      "mensaje_error": "En Java, la JVM elige el método según el tipo REAL del objeto, no según la referencia. El objeto es Perro, así que se llama Perro.hablar().",
      "recomendacion": "Repasa herencia, @Override y polimorfismo en Java — Unidad 3."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 27,
    "fields": {
      "ejercicio": 35,
      "mensaje_correcto": "¡Exacto! 4 + 7 + 2 + 9 + 3 = 25. El for-each recorre todos los elementos sin necesidad de índice.",
      "mensaje_error": "Suma manualmente: 4 + 7 + 2 + 9 + 3 = ?",
      "recomendacion": "Repasa arreglos y ciclos for-each en Java — Unidad 4."
    }
  },
  {
    "model": "ejercicios.retroalimentacion",
    "pk": 28,
    "fields": {
      "ejercicio": 36,
      "mensaje_correcto": "¡Perfecto! El algoritmo burbuja deja el arreglo {1, 3, 5, 7, 9}. numeros[0] = 1 es el menor.",
      "mensaje_error": "El ordenamiento burbuja deja el arreglo ordenado de menor a mayor: {1, 3, 5, 7, 9}. numeros[0] siempre será el menor.",
      "recomendacion": "Traza el burbuja manualmente con el arreglo dado. Repasa U4: Arreglos."
    }
  }
```

- [ ] **Step 2: Validar JSON y conteos finales**

```bash
python -c "import json; data = json.load(open('fixtures/datos_iniciales.json', encoding='utf-8')); print(f'Total objects: {len(data)}'); print(f'Ejercicios Java total: {sum(1 for o in data if o[\"model\"] == \"ejercicios.ejercicio\" and o[\"fields\"].get(\"lenguaje\") == \"java\")}'); print(f'Retros nuevas: {sum(1 for o in data if o[\"model\"] == \"ejercicios.retroalimentacion\" and o[\"pk\"] >= 19)}')"
```

Resultado esperado:

```
Total objects: 65
Ejercicios Java total: 13
Retros nuevas: 10
```

(65 = 4 temas + 39 ejercicios + 22 retros + 0 = revisado: 4+26+15+0 = 45 antes; +13 ejercicios Java +10 retros = 68. **Revisión de conteo**: el fixture pre-existente tiene 4 temas + 26 ejercicios + 18 retros = 48 objetos. Tras Java: 48 + 13 + 10 = **71 objetos**.)

(Si el conteo es 71, está correcto. Ajusta el assertion mental — el comando muestra el número real.)

- [ ] **Step 3: Commit**

```bash
git add fixtures/datos_iniciales.json
git commit -m "feat(fixtures): add retroalimentaciones for 10 Java interactive exercises"
```

---

## Task 11: Verificación final end-to-end

**Files:** ninguno modificado en este task (solo verificación)

- [ ] **Step 1: Verificar Django check completo**

```bash
python manage.py check
```

Resultado esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 2: Verificar que no hay migraciones pendientes**

```bash
python manage.py makemigrations --check --dry-run
```

Resultado esperado: `No changes detected` y exit code 0.

- [ ] **Step 3: Cargar el fixture**

```bash
python manage.py loaddata fixtures/datos_iniciales.json
```

Resultado esperado: una línea como `Installed 71 object(s) from 1 fixture(s)` (el número exacto puede variar según objetos creados manualmente, pero debe terminar sin errores).

- [ ] **Step 4: Verificar conteos en la base de datos via shell**

```bash
python manage.py shell -c "from apps.ejercicios.models import Ejercicio; print('Java interactivos:', Ejercicio.objects.filter(lenguaje='java', categoria='interactivo').count()); print('Java resueltos:', Ejercicio.objects.filter(lenguaje='java', categoria='resuelto').count()); print('Total Java:', Ejercicio.objects.filter(lenguaje='java').count())"
```

Resultado esperado:

```
Java interactivos: 10
Java resueltos: 3
Total Java: 13
```

- [ ] **Step 5: Verificar conteos por unidad y dificultad**

```bash
python manage.py shell -c "from apps.ejercicios.models import Ejercicio; from collections import Counter; ejs = Ejercicio.objects.filter(lenguaje='java'); print('Por unidad:', Counter(e.tema.unidad for e in ejs)); print('Por dificultad:', Counter(e.dificultad for e in ejs))"
```

Resultado esperado:

```
Por unidad: Counter({2: 5, 3: 3, 4: 3, 1: 2})
Por dificultad: Counter({'basico': 5, 'medio': 4, 'avanzado': 4})
```

- [ ] **Step 6: Verificar que C++ y Python siguen intactos**

```bash
python manage.py shell -c "from apps.ejercicios.models import Ejercicio; print('C++:', Ejercicio.objects.filter(lenguaje='cpp').count()); print('Python:', Ejercicio.objects.filter(lenguaje='python').count())"
```

Resultado esperado (sin cambios respecto al estado previo):

```
C++: 17
Python: 8
```

(17 = 9 originales con default cpp + 3 C++ explícitos pk 18-20 + 5 resueltos pk 21,22,23,24,25,26 = 9+3+5 = 17. Python = 8 = pks 10,11,12,13,14,15,16,17.)

Si el conteo difiere, revisar si algún ejercicio antiguo cambió de lenguaje involuntariamente.

- [ ] **Step 7: Levantar el servidor y probar manualmente en el navegador**

```bash
python manage.py runserver
```

En el navegador abrir y verificar:

| URL | Qué verificar |
|-----|---------------|
| `http://127.0.0.1:8000/ejercicios/practica/?lenguaje=java` | Lista 10 ejercicios Java con chip ☕ Java; botón Java está activo |
| `http://127.0.0.1:8000/ejercicios/practica/27/` (Saludo con Scanner) | Login si pide. Badge "Java 11", archivo "referencia.java", syntax highlight Java, texto "Basándote en el código Java" |
| Responder "Hola, Ana!" en el ejercicio 27 | Retroalimentación correcta aparece |
| `http://127.0.0.1:8000/ejercicios/resueltos/?lenguaje=java` | Lista 3 ejercicios Java con filtro Java activo y chip ☕ Java |
| `http://127.0.0.1:8000/ejercicios/resueltos/37/` (Estructura básica Java) | Badge "Java 11", archivo `.java`, código bien resaltado |
| `http://127.0.0.1:8000/ejercicios/practica/?lenguaje=cpp` | C++ sigue funcionando idéntico |
| `http://127.0.0.1:8000/ejercicios/practica/?lenguaje=python` | Python sigue funcionando idéntico |
| `http://127.0.0.1:8000/ejercicios/practica/` (sin filtro) | Muestra todos los lenguajes |

Detener el servidor con `Ctrl+C` después de verificar.

- [ ] **Step 8: Commit final (si hubo ajustes en los pasos anteriores)**

Si los pasos 1-7 pasaron sin necesidad de ajustes, no hay nada que commitear. Si fue necesario corregir algo (p. ej. un typo en una solucion_esperada), commitea el fix:

```bash
git status   # verificar si hay cambios
# Si los hay:
git add -p   # revisar cambios línea por línea
git commit -m "fix(ejercicios): adjustments after manual QA"
```

---

## Self-Review (completado por el autor del plan)

**Spec coverage:**
- ✅ Sección 4.1 (Modelo) → Task 1
- ✅ Sección 4.2 (Migración) → Task 1
- ✅ Sección 4.3 (Vistas) → Task 2
- ✅ Sección 4.4 (Plantillas) → Tasks 3, 4, 5, 6
- ✅ Sección 4.5 (Fixture) → Tasks 7, 8, 9, 10
- ✅ Sección 5 (Lista de ejercicios) → 13 ejercicios cubiertos
- ✅ Sección 8 (Verificación) → Task 11

**Placeholder scan:** Ningún TBD/TODO. Todos los pasos tienen código completo o comandos exactos.

**Type consistency:**
- `lenguaje='java'` consistente en todos los ejercicios
- pks consecutivos 27–39 (ejercicios) y 19–28 (retros)
- FKs `tema` validadas: U1→1, U2→2, U3→3, U4→4
- Estilo Java consistente (`public class`, `System.out.println`, `Scanner`)

Plan listo para ejecución.
