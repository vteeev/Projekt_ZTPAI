# System zarządzania finansami osobistymi

REST API do zarządzania finansami osobistymi: transakcje (przychody/wydatki), kategorie,
budżety miesięczne, wykresy, eksport PDF/CSV oraz analiza AI wydatków.

Projekt indywidualny realizowany w **Django + Django REST Framework** (kryteria opisane
dla Spring Boot — mapowanie technologii w [PLAN_PROJEKTU.md](PLAN_PROJEKTU.md)).

## Stos technologiczny

| Warstwa        | Technologia                                  |
|----------------|----------------------------------------------|
| Backend        | Django 5 + Django REST Framework             |
| Baza danych    | PostgreSQL 16                                |
| Autoryzacja    | JWT (`djangorestframework-simplejwt`)        |
| Kolejki / jobs | Celery + Redis                               |
| Dokumentacja   | drf-spectacular (Swagger UI)                 |
| Frontend       | React (Vite) + Chart.js *(kolejne etapy)*    |
| Uruchomienie   | Docker Compose                               |

## Struktura projektu

```
config/            # konfiguracja projektu Django
  settings/        # base / dev / prod
  celery.py        # konfiguracja Celery
apps/
  core/            # health-check, obsługa błędów, narzędzia współdzielone
manage.py
docker-compose.yml
```

## Uruchomienie (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Domyślnie web nasłuchuje na porcie 8000. Jeśli jest zajęty, ustaw w `.env`:
`WEB_PORT=8001`.

Aplikacja: <http://localhost:8000> · Swagger: <http://localhost:8000/api/docs/>

Health-check:

```bash
curl http://localhost:8000/api/health/
# {"status": "ok", "database": "connected"}
```

## Przydatne komendy

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py migrate
docker compose exec web pytest
```

## Postęp prac

Status etapów: [PLAN_PROJEKTU.md](PLAN_PROJEKTU.md).

- [x] Etap 0 — Setup środowiska (Docker, szkielet Django+DRF)
- [x] Etap 1 — Działający Django + baza + health-check + admin
- [x] Etap 2 — CRUD encji Transaction (ocena 3.0 osiągnięta)
- [ ] Etap 3 — Warstwy, DTO, walidacja, obsługa błędów
- [ ] Etap 4 — Security JWT
- [ ] Etap 5 — Domena (kategorie, budżety, statystyki)
- [ ] Etap 6 — Celery (raporty, eksport, AI)
- [ ] Etap 7 — Events (signals)
- [ ] Etap 8 — Testy jednostkowe
- [ ] Etap 9 — Czysty kod
- [ ] Etap 10 — Frontend React
- [ ] Etap 11 — Dokumentacja + demo
