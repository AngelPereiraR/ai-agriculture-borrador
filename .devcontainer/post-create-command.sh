pip install -r /workspaces/ai-agriculture/requirements.txt
pip install pre-commit

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
pre-commit run -a
EOF
chmod +x .git/hooks/pre-commit


# --- CONFIGURACIÓN AUTOMÁTICA ---

echo "⏳ Esperando a que la base de datos (db:5432) esté disponible..."
until python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('db', 5432))" 2>/dev/null; do
  echo "   ...esperando a DB..."
  sleep 2
done
echo "✅ Base de datos conectada."

echo "🗄️ Aplicando migraciones..."
python src/manage.py migrate

echo "👤 Creando superusuario (si no existe)..."
# Django lee las variables del .env automáticamente
python src/manage.py createsuperuser --noinput 2>/dev/null || echo "   (El superusuario ya existe o faltan variables)"

echo "🎉 ¡Entorno configurado correctamente!"

echo "✅ Marcando entorno como listo..."
touch /tmp/workspace_ready
