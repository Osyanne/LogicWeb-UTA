#!/usr/bin/env bash
# Build script de Render para LogicWeb UTA.
# Render lo ejecuta en cada deploy.
set -o errexit

pip install -r requirements.txt

# Recolectar estáticos (CSS/JS) para que WhiteNoise los sirva.
python manage.py collectstatic --no-input

# Aplicar migraciones a la base de datos.
python manage.py migrate

# Sembrar/actualizar el contenido (temas, ejercicios, pistas). Idempotente por PK.
python manage.py loaddata fixtures/datos_iniciales.json
