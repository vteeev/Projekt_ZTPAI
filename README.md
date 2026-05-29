# System zarządzania finansami osobistymi

REST API + SPA do zarządzania finansami osobistymi: transakcje (przychody/wydatki),
kategorie, budżety miesięczne, wykresy, eksport PDF/CSV oraz analiza AI wydatków.

Projekt indywidualny realizowany w **Django + Django REST Framework** (kryteria opisane
dla Spring Boot — pełne mapowanie technologii w [PLAN_PROJEKTU.md](PLAN_PROJEKTU.md)).

## Funkcje

- 🔐 Rejestracja i logowanie (JWT)
- 💸 CRUD transakcji (przychody / wydatki) z izolacją per użytkownik
- 🏷️ Kategorie transakcji (własne, kolorowane)
- 📊 Dashboard z wykresami (wydatki wg kategorii, trend miesięczny)
- 🎯 Budżety miesięczne z wyliczanym wykorzystaniem
- 📄 Eksport CSV i PDF (asynchronicznie przez Celery)
- 🤖 Analiza AI wydatków (heurystyka lub Claude API)
- 🔔 Powiadomienia o przekroczeniu budżetu (Django signals)

## Stos technologiczny

| Warstwa        | Technologia                                  |
|----------------|----------------------------------------------|
| Backend        | Django 5 + Django REST Framework             |
| Baza danych    | PostgreSQL 16 (Django ORM)                   |
| Autoryzacja    | JWT (`djangorestframework-simplejwt`)        |
| Kolejki / jobs | Celery + Redis                               |
| Events         | Django signals                               |
| Dokumentacja   | drf-spectacular (Swagger UI)                 |
| Frontend       | React 18 + Vite + Chart.js + Axios           |
| Testy          | pytest-django (19 testów)                    |
| Jakość kodu    | black + isort + ruff + pre-commit            |
| Uruchomienie   | Docker Compose                               |

## Architektura warstwowa

```
apps/
  accounts/        # rejestracja, JWT, profil
  core/            # health-check, jednolita obsługa błędów
  finance/
    models.py      # encje (Transaction, Category, Budget, Report, Notification)
    selectors.py   # warstwa odczytu (≈ Repository) + agregacje statystyk
    services.py    # warstwa logiki biznesowej (Service)
    serializers.py # DTO + walidacja
    views.py       # ViewSet/APIView (Controller) - cienkie
    tasks.py       # zadania Celery (raporty, AI)
    signals.py     # events domenowe
config/
  settings/        # base / dev / prod
  celery.py
frontend/          # aplikacja React (Vite)
```

## Uruchomienie

### Backend (Docker)

```bash
cp .env.example .env
docker compose up --build       # web + db + redis + worker
docker compose exec web python manage.py createsuperuser
```

- API: <http://localhost:8000> (lub `WEB_PORT` z `.env`)
- Swagger: <http://localhost:8000/api/docs/>
- Panel admina: <http://localhost:8000/admin/>

> Jeśli port 8000 jest zajęty, ustaw w `.env` np. `WEB_PORT=8001`.

### Frontend (React)

```bash
cd frontend
cp .env.example .env            # ustaw VITE_API_URL na adres API
npm install
npm run dev                     # http://localhost:5173
```

## Przegląd API

| Metoda          | Endpoint                       | Opis                            |
|-----------------|--------------------------------|---------------------------------|
| POST            | `/api/auth/register/`          | Rejestracja                     |
| POST            | `/api/auth/login/`             | Login → access + refresh        |
| POST            | `/api/auth/refresh/`           | Odświeżenie tokenu              |
| GET             | `/api/auth/me/`                | Profil zalogowanego             |
| GET/POST        | `/api/transactions/`           | Lista / dodawanie transakcji    |
| GET/PATCH/DELETE| `/api/transactions/{id}/`      | Szczegóły / edycja / usunięcie  |
| GET/POST        | `/api/categories/`             | Kategorie                       |
| GET/POST        | `/api/budgets/`                | Budżety (z `spent`/`usage`)     |
| POST            | `/api/reports/`                | Zlecenie raportu CSV/PDF/AI     |
| GET             | `/api/reports/{id}/download/`  | Pobranie pliku raportu          |
| GET             | `/api/notifications/`          | Powiadomienia użytkownika       |
| GET             | `/api/stats/summary/`          | Przychody/wydatki/bilans        |
| GET             | `/api/stats/by-category/`      | Wydatki wg kategorii (wykres)   |
| GET             | `/api/stats/monthly/`          | Trend roczny (wykres)           |
| GET             | `/api/health/`                 | Health-check                    |

## Testy

```bash
docker compose exec web pytest
```

## Spełnienie kryteriów oceny

| Kryterium (Spring Boot → Django)               | Status | Gdzie                                    |
|------------------------------------------------|:------:|------------------------------------------|
| **3.0** Działający backend + baza              | ✅ | Django + PostgreSQL (Docker)                  |
| **3.0** CRUD dla encji                         | ✅ | `Transaction` (+ Category/Budget)             |
| **4.0** Struktura warstwowa                    | ✅ | views / services / selectors / models         |
| **4.0** DTO + walidacja                        | ✅ | DRF serializers (`validate_*`)                |
| **4.0** Obsługa błędów                         | ✅ | `core/exceptions.py` (jednolity JSON)         |
| **4.0** Security (JWT)                          | ✅ | simplejwt + izolacja per-user                 |
| **5.0** Unit testy                              | ✅ | pytest-django (19 testów)                     |
| **5.0** Events LUB Kolejki                      | ✅ | **Celery + Redis** *oraz* **signals**         |
| **5.0** Czysty kod                              | ✅ | black + isort + ruff + pre-commit             |
| **5.0** Frontend konsumujący API               | ✅ | React (Vite) + Chart.js                       |

Scenariusz demo: [DEMO.md](DEMO.md).

## Postęp prac (historia w commitach)

- [x] Etap 0 — Setup środowiska (Docker, szkielet Django+DRF)
- [x] Etap 1 — Działający Django + baza + health-check + admin
- [x] Etap 2 — CRUD encji Transaction (ocena 3.0 osiągnięta)
- [x] Etap 3 — Warstwy, DTO, walidacja, obsługa błędów
- [x] Etap 4 — Security JWT (ocena 4.0 osiągnięta)
- [x] Etap 5 — Domena (kategorie, budżety, statystyki)
- [x] Etap 6 — Celery (raporty, eksport, AI)
- [x] Etap 7 — Events (signals)
- [x] Etap 8 — Testy jednostkowe (19 testów)
- [x] Etap 9 — Czysty kod (black/isort/ruff/pre-commit)
- [x] Etap 10 — Frontend React (ocena 5.0 osiągnięta)
- [x] Etap 11 — Dokumentacja + Swagger + scenariusz demo
