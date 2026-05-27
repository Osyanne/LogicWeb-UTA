# Diseño: Soporte para ejercicios en Java

**Fecha:** 2026-05-27
**Proyecto:** LogicWeb UTA — Django
**Autor:** Brainstorming Claude + Imanol Miranda
**Estado:** Aprobado para implementación

---

## 1. Contexto

El proyecto LogicWeb UTA es una plataforma educativa para enseñanza de programación en la Universidad Técnica de Ambato. Actualmente la app `ejercicios` soporta dos lenguajes:

- **C++** (predeterminado) — 7 ejercicios interactivos + 2 resueltos
- **Python** — 5 ejercicios interactivos

El ingeniero del proyecto solicitó agregar soporte para **Java** como tercer lenguaje, manteniendo la consistencia con la estructura existente.

## 2. Objetivo

Extender la app `ejercicios` para soportar el lenguaje Java, incluyendo:

- Campo `lenguaje='java'` en el modelo `Ejercicio`
- 13 ejercicios Java pre-cargados (10 interactivos + 3 resueltos) cubriendo las 4 unidades temáticas
- Renderizado correcto en plantillas (etiquetas, badges, syntax highlighting)
- Filtro de lenguaje en listas de ejercicios

Sin alterar el comportamiento existente de C++ ni Python.

## 3. Arquitectura

El diseño extiende capas existentes sin agregar nuevas. Cuatro áreas de cambio:

```
┌─────────────────────────────────────────┐
│  apps/ejercicios/models.py              │  ← agregar 'java' a LENGUAJES
│  apps/ejercicios/migrations/0004_*.py   │  ← migración de campo choices
│  apps/ejercicios/views.py               │  ← filtro lenguaje en resueltos
│  apps/ejercicios/fixtures/*.json        │  ← +13 ejercicios + +13 feedback
├─────────────────────────────────────────┤
│  templates/ejercicios/interactivo.html  │  ← if/elif/else (Python/Java/C++)
│  templates/ejercicios/resuelto.html     │  ← if/elif/else (idem)
│  templates/ejercicios/lista_*.html      │  ← filtro y chip de Java
└─────────────────────────────────────────┘
```

## 4. Componentes

### 4.1 Modelo (`apps/ejercicios/models.py`)

Cambio único en el campo `LENGUAJES` del modelo `Ejercicio`:

```python
LENGUAJES = [
    ('cpp', 'C++'),
    ('python', 'Python'),
    ('java', 'Java'),  # ← nuevo
]
lenguaje = models.CharField(max_length=10, choices=LENGUAJES, default='cpp')
```

El campo `codigo_cpp` se conserva con su nombre actual (contiene el código en cualquier lenguaje, según `lenguaje`). El método `evaluar()` no depende del lenguaje — funciona idéntico para Java.

### 4.2 Migración (`migrations/0004_add_java_to_ejercicio_lenguaje.py`)

Migración generada automáticamente por `makemigrations`. Solo modifica el atributo `choices` del campo. Sin operaciones de datos. Reversible.

### 4.3 Vistas (`apps/ejercicios/views.py`)

La vista `ejercicios_interactivos` **ya soporta** filtro por lenguaje — sin cambios.

La vista `ejercicios_resueltos` no soporta filtro de lenguaje. Agregar de forma análoga:

```python
def ejercicios_resueltos(request):
    ejercicios = Ejercicio.objects.filter(categoria='resuelto', activo=True).select_related('tema')
    lenguaje_filtro = request.GET.get('lenguaje')
    unidad_filtro   = request.GET.get('unidad')
    if lenguaje_filtro:
        ejercicios = ejercicios.filter(lenguaje=lenguaje_filtro)
    if unidad_filtro:
        ejercicios = ejercicios.filter(tema__unidad=unidad_filtro)
    return render(request, 'ejercicios/lista_resueltos.html', {
        'ejercicios': ejercicios,
        'lenguaje_filtro': lenguaje_filtro,
        'unidad_filtro': unidad_filtro,
    })
```

### 4.4 Plantillas

#### `templates/ejercicios/interactivo.html`
Convertir los `{% if/else %}` de Python/C++ a `{% if/elif/else %}` con rama Java:

```django
{% if ejercicio.lenguaje == 'python' %}
  <h3>★ Código Python — Estúdialo antes de responder</h3>
{% elif ejercicio.lenguaje == 'java' %}
  <h3>★ Código Java — Estúdialo antes de responder</h3>
{% else %}
  <h3>★ Código C++ — Estúdialo antes de responder</h3>
{% endif %}
```

Aplicar el mismo patrón para:
- `lang-label`: `referencia.java`
- `badge-cpp`: `Java 11`
- Clase Prism: `language-java`
- Texto "Basándote en el código Java"

#### `templates/ejercicios/resuelto.html`
Actualmente hardcoded a C++ (no contempla ni Python ni Java). Convertir a `{% if/elif/else %}`:
- Título: "Código Java — Solución"
- `lang-label`: `{{ ejercicio.titulo|truncatechars:40 }}.java`
- `badge-cpp`: `Java 11`
- Clase Prism: `language-java`

#### `templates/ejercicios/lista_interactivos.html`
Agregar botón de filtro Java junto a C++ y Python (color `#b07219` — GitHub Java):

```django
<a href="?lenguaje=java{% if unidad_filtro %}&unidad={{ unidad_filtro }}{% endif %}"
   class="btn btn-sm {% if lenguaje_filtro == 'java' %}btn-primary{% else %}btn-outline{% endif %}"
   style="border-color:#b07219;{% if lenguaje_filtro == 'java' %}background:#b07219;color:#fff;{% endif %}">☕ Java</a>
```

Agregar chip Java en la tarjeta del ejercicio (extender el `{% if/elif/else %}`).

#### `templates/ejercicios/lista_resueltos.html`
- Agregar filtro de lenguaje (no lo tiene — solo tiene filtro por unidad)
- Agregar chip de lenguaje en la tarjeta
- Cambiar título "💡 Ejercicios Resueltos — Código C++" → "💡 Ejercicios Resueltos — Código paso a paso"
- Cambiar texto del botón "Ver código C++ →" → "Ver solución →"

### 4.5 Fixture (`apps/ejercicios/fixtures/datos_iniciales.json`)

Agregar 13 objetos `ejercicios.ejercicio` + 13 objetos `ejercicios.retroalimentacion`. Los pk se asignan consecutivos a partir del primero libre (durante la implementación se inspecciona el fixture para encontrar el último pk en uso y se continúa desde ahí).

## 5. Ejercicios Java a crear

### Interactivos (10)

| # | Unidad | Título | Dificultad | Tipo respuesta |
|---|--------|--------|------------|----------------|
| 1 | U1 | Saludo con Scanner | básico | texto |
| 2 | U2 | Suma de dos enteros | básico | entero |
| 3 | U2 | Promedio de tres notas | básico | decimal |
| 4 | U2 | Mayor de tres números | básico | entero |
| 5 | U2 | Factorial con while | medio | entero |
| 6 | U2 | Fibonacci recursivo | avanzado | entero |
| 7 | U3 | Clase Estudiante (POO) | medio | decimal |
| 8 | U3 | Herencia: Animal/Perro con polimorfismo | avanzado | texto |
| 9 | U4 | Suma de elementos de un arreglo | medio | entero |
| 10 | U4 | Ordenamiento burbuja | avanzado | entero |

### Resueltos (3)

| # | Unidad | Título | Dificultad |
|---|--------|--------|------------|
| 11 | U1 | Estructura básica de un programa Java | básico |
| 12 | U3 | POO en Java: clase con constructor y métodos | medio |
| 13 | U4 | Búsqueda binaria con ArrayList | avanzado |

**Distribución por dificultad:** 5 básicos, 4 medios, 4 avanzados (10 interactivos + 3 resueltos).

### Estilo de código Java
- Java estándar con `Scanner` para entrada
- Java 11 (compatible con cursos universitarios introductorios)
- Sin Stream API ni Lambda — bucles tradicionales para mantener nivel introductorio
- Convenciones: PascalCase para clases, camelCase para variables/métodos
- Cada ejercicio incluye una clase pública con `main` (los POO también, dentro de la misma clase)

## 6. Flujo de datos

El flujo existente funciona sin modificaciones:

1. Estudiante navega `/ejercicios/practica/?lenguaje=java`
2. Vista filtra `Ejercicio.objects.filter(lenguaje='java', categoria='interactivo', activo=True)`
3. Plantilla `lista_interactivos.html` renderiza tarjetas con chip Java
4. Estudiante selecciona ejercicio → `ejercicio_interactivo_detalle(pk)`
5. Plantilla `interactivo.html` detecta `ejercicio.lenguaje == 'java'` → muestra código con highlight Java
6. Estudiante envía respuesta → `Ejercicio.evaluar(respuesta)` (lógica independiente del lenguaje)
7. Se crea `Intento` → signal actualiza `ProgresoEstudiante`

## 7. Manejo de errores

Sin cambios. El sistema actual maneja correctamente:
- Respuesta vacía: `RespuestaForm.clean_respuesta()` rechaza
- Respuesta inválida (tipo): `Ejercicio.evaluar()` retorna `False`
- Ejercicio inactivo: `get_object_or_404` con `activo=True`

Si un usuario fuerza un `?lenguaje=xxx` inválido en URL, el queryset filtra a vacío y se muestra "No hay ejercicios para los filtros seleccionados".

## 8. Pruebas / Verificación

### Verificación funcional manual
1. `python manage.py migrate` ejecuta sin errores
2. `python manage.py loaddata datos_iniciales` carga los 13 nuevos ejercicios
3. Visitar `/ejercicios/practica/?lenguaje=java` → lista los 10 interactivos
4. Abrir cualquier ejercicio Java → código se ve con badge `Java 11`, archivo `.java`, highlighting Java
5. Responder correctamente un ejercicio → mensaje de retroalimentación correcto
6. Visitar `/ejercicios/resueltos/?lenguaje=java` → lista los 3 resueltos
7. Visitar `/ejercicios/practica/?lenguaje=cpp` y `?lenguaje=python` → siguen funcionando idéntico
8. Visitar `/ejercicios/practica/` sin filtro → muestra todos los lenguajes

### Verificación de regresión
- Los ejercicios C++ y Python existentes siguen renderizando con sus badges originales
- Los `Intento` y `ProgresoEstudiante` previos no se ven afectados
- Las pruebas existentes (si las hay) siguen pasando

## 9. Decisiones de diseño

**¿Por qué fixture en lugar de admin?**
Para que los ejercicios queden versionados en git y cualquier miembro del equipo pueda recargarlos en una instalación fresh. Sigue la convención existente (C++ y Python también están en el fixture).

**¿Por qué no cambiar el nombre del campo `codigo_cpp` a algo neutral?**
Sería un refactor mayor (modelo, migración con `RenameField`, signals, vistas, plantillas, contextos). Está fuera del alcance de esta tarea. Se documenta como deuda técnica menor.

**¿Por qué Java 11 y no Java 17/21?**
Java 11 es el LTS más enseñado en universidades de Ecuador y mantiene compatibilidad con la mayoría de IDEs educativos (BlueJ, JCreator, IntelliJ Community).

**¿Por qué color `#b07219`?**
Es el color oficial de Java en GitHub Linguist, consistente con cómo identifica el lenguaje el resto de la industria.

## 10. Fuera de alcance

- Renombrar `codigo_cpp` → `codigo_fuente` (refactor mayor, no afecta funcionalidad)
- Ejecutar código Java en el servidor (el código es educativo, nunca se ejecuta)
- Editor con autocompletado Java en el formulario de respuesta
- Tests automatizados (el proyecto no tiene suite de tests; se verifica manualmente)
- Ejercicios Java para U1 más allá de "Saludo con Scanner" (U1 es algoritmos/pseudocódigo, no requiere ejercicios de código por lenguaje)
