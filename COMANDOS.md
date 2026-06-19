# ⚡ Comandos útiles — Vittorio Coffee

## ▶️ Correr el servidor
```bash
cd ~/Desktop/DJANGO
source venv/bin/activate        # activa el entorno virtual (verás "(venv)" en el prompt)
python manage.py runserver      # levanta el server
# Abrir: http://localhost:8000/
# Detener: Ctrl + C
```
> El `venv` se activa una vez por terminal. Si abrís una nueva, repetí `source venv/bin/activate`.

## 🐍 Comandos de Django (los más usados)
```bash
python manage.py runserver          # levantar el server
python manage.py makemigrations     # crear migraciones (tras cambiar models.py)
python manage.py migrate            # aplicar migraciones (crear/actualizar tablas)
python manage.py createsuperuser    # crear un usuario administrador
python manage.py check              # validar el proyecto (sin levantarlo)
python manage.py shell              # consola Python con Django cargado
```

## 🌱 Git — primera vez (esta carpeta todavía no es repo)
```bash
cd ~/Desktop/DJANGO
git init
git add .
git commit -m "Primer commit: tienda web cafetería en Django"
```

## ☁️ Git — subir a GitHub (opcional)
```bash
# 1) Creá un repo vacío en github.com, después:
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

## 🔁 Git — día a día (después del primer commit)
```bash
git status                          # ver qué cambió
git add .                           # preparar todos los cambios
git commit -m "describí el cambio"  # guardar el commit
git push                            # subir a GitHub
```

## 🧪 Recrear todo desde cero (si hace falta)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🔑 Credenciales de prueba
- Admin:  `admin` / `Cafe2024Admin`  → panel en /panel/
- Cliente: `cliente` / `Cafe2024Cliente`
