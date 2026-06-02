from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Tema, Ejercicio, Intento, Retroalimentacion
from .forms import RespuestaForm


# ══════════════════════════════════════════════════════════════
#  INICIO
# ══════════════════════════════════════════════════════════════
def inicio(request):
    unidades = Tema.objects.values('unidad').distinct().order_by('unidad')
    total_ejercicios = Ejercicio.objects.filter(activo=True).count()
    return render(request, 'inicio/index.html', {
        'unidades': unidades,
        'total_ejercicios': total_ejercicios,
    })


# ══════════════════════════════════════════════════════════════
#  EJERCICIOS RESUELTOS
# ══════════════════════════════════════════════════════════════
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


def ejercicio_resuelto_detalle(request, pk):
    ejercicio = get_object_or_404(Ejercicio, pk=pk, categoria='resuelto', activo=True)
    if request.user.is_authenticated:
        Intento.objects.get_or_create(
            usuario=request.user,
            ejercicio=ejercicio,
            defaults={'respuesta_usuario': 'visto', 'resultado': 'correcto'},
        )
    return render(request, 'ejercicios/resuelto.html', {
        'ejercicio': ejercicio,
        'codigo_cpp': ejercicio.codigo_cpp,
    })


# ══════════════════════════════════════════════════════════════
#  EJERCICIOS INTERACTIVOS
# ══════════════════════════════════════════════════════════════
def ejercicios_interactivos(request):
    ejercicios = Ejercicio.objects.filter(categoria='interactivo', activo=True).select_related('tema')
    lenguaje_filtro = request.GET.get('lenguaje')
    unidad_filtro   = request.GET.get('unidad')
    if lenguaje_filtro:
        ejercicios = ejercicios.filter(lenguaje=lenguaje_filtro)
    if unidad_filtro:
        ejercicios = ejercicios.filter(tema__unidad=unidad_filtro)
    return render(request, 'ejercicios/lista_interactivos.html', {
        'ejercicios': ejercicios,
        'lenguaje_filtro': lenguaje_filtro,
        'unidad_filtro': unidad_filtro,
    })


@login_required
def ejercicio_interactivo_detalle(request, pk):
    ejercicio = get_object_or_404(Ejercicio, pk=pk, categoria='interactivo', activo=True)
    form = RespuestaForm()

    if request.method == 'POST':
        form = RespuestaForm(request.POST)
        if form.is_valid():
            respuesta   = form.cleaned_data['respuesta']
            es_correcto = ejercicio.evaluar(respuesta)
            resultado   = 'correcto' if es_correcto else 'incorrecto'

            intento = Intento.objects.create(
                usuario=request.user,
                ejercicio=ejercicio,
                respuesta_usuario=respuesta,
                resultado=resultado,
            )
            retro = getattr(ejercicio, 'retroalimentacion', None)

            return render(request, 'retroalimentacion/respuesta.html', {
                'ejercicio': ejercicio,
                'intento': intento,
                'es_correcto': es_correcto,
                'retro': retro,
                'codigo_cpp': ejercicio.codigo_cpp,
            })

    return render(request, 'ejercicios/interactivo.html', {
        'ejercicio': ejercicio,
        'codigo_cpp': ejercicio.codigo_cpp,
        'form': form,
        'pistas': ejercicio.pistas.order_by('orden'),
    })
