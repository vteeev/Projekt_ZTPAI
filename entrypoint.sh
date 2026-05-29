#!/bin/sh
set -e

# Czekaj na baze danych
echo "Czekam na PostgreSQL ($POSTGRES_HOST:$POSTGRES_PORT)..."
while ! python -c "import socket,os,sys; s=socket.socket(); \
    s.settimeout(1); \
    sys.exit(0) if s.connect_ex((os.environ.get('POSTGRES_HOST','db'), int(os.environ.get('POSTGRES_PORT','5432'))))==0 else sys.exit(1)" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL dostepny."

# Migracje (tylko dla procesu web; worker pomija)
if [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Uruchamiam migracje..."
    python manage.py migrate --noinput
fi

exec "$@"
