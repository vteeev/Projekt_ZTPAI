# System zarządzania finansami osobistymi — plan implementacji

> Projekt indywidualny (§5). Kryteria oryginalnie opisane dla **Spring Boot + REST API**.
> My realizujemy go w **Python / Django + Django REST Framework**, dlatego poniżej znajduje się
> mapowanie każdego kryterium na odpowiednik z ekosystemu Django, a następnie plan podzielony na etapy.

---

## 1. Analiza założeń

### Funkcje aplikacji (z opisu projektu)
- Logowanie / rejestracja użytkownika
- Dodawanie wydatków i przychodów (transakcje)
- Kategorie transakcji
- Wykresy (dashboard analityczny)
- Budżety miesięczne
- Eksport PDF / CSV
- Analiza AI wydatków
- (opcjonalnie) Płatności Stripe

### Co projekt pokazuje w portfolio
CRUD • autoryzacja • dashboard • analityka • background jobs • REST API

---

## 2. Stos technologiczny (adaptacja do Pythona)

| Warstwa            | Technologia                                              |
|--------------------|---------------------------------------------------------|
| Backend            | Django + Django REST Framework (DRF)                     |
| Baza danych        | PostgreSQL (Django ORM)                                  |
| Autoryzacja        | JWT — `djangorestframework-simplejwt`                    |
| Kolejki / jobs     | Celery + Redis (broker) — raporty, eksport, analiza AI   |
| Events             | Django signals (zdarzenia domenowe)                      |
| Wykresy            | Chart.js (po stronie frontendu)                          |
| Frontend           | **React (Vite)** + Axios + Chart.js                      |
| Eksport            | PDF: `WeasyPrint`/`ReportLab`, CSV: wbudowany `csv`      |
| Analiza AI         | API Anthropic/OpenAI lub heurystyka (fallback bez klucza)|
| Testy              | `pytest-django` + DRF `APITestCase`                      |
| Jakość kodu        | `black`, `isort`, `flake8`/`ruff`, `pre-commit`          |
| Uruchomienie       | Docker Compose (web + db + redis + worker)               |
| Płatności (opcja)  | Stripe                                                   |

> **Dlaczego React, a nie Angular?** Kryterium dopuszcza „prostą aplikację konsumującą API”.
> React (Vite) jest lżejszy do startu, lepiej wygląda w portfolio i równie dobrze spełnia wymaganie
> frontendu konsumującego REST API.

---

## 3. Mapowanie kryteriów oceny: Spring Boot → Django

| Kryterium (oryginał Spring Boot)              | Odpowiednik w Django/DRF                                         |
|-----------------------------------------------|-----------------------------------------------------------------|
| Działający Spring Boot                         | Działający projekt Django + DRF (serwer dev / Docker)           |
| Połączenie z bazą danych                       | PostgreSQL przez Django ORM                                      |
| CRUD dla 1 encji                               | CRUD na encji `Transaction` (i kolejnych)                       |
| Struktura warstwowa Controller/Service/Repo    | **ViewSet** (≈Controller) / warstwa **services.py** / **Model + Manager** (≈Repository) |
| DTO + Walidacja danych                         | DRF **Serializers** + walidacja (`validate_*`, validators)      |
| Obsługa błędów                                 | Custom `exception_handler` DRF + spójny format błędów          |
| Security (JWT lub Basic Auth)                  | **JWT** (`simplejwt`) z access/refresh token                   |
| Unit testy                                     | `pytest-django` / `APITestCase`                                 |
| Events LUB Kolejki (Rabbit/Kafka)              | **Celery + Redis** (kolejki) **oraz** Django **signals** (events)|
| Czysty kod                                     | `black` + `isort` + `ruff` + `pre-commit`, typowanie           |
| Frontend (Angular konsumujący API)             | **React (Vite)** konsumujący REST API                          |

---

## 4. Model danych (szkic)

```
User (Django auth)
 └─ 1:N Category        (name, type[INCOME|EXPENSE], color, user)
 └─ 1:N Transaction     (amount, type, date, description, category FK, user)
 └─ 1:N Budget          (month, year, amount, category FK?, user)
 └─ 1:N Report          (type, status, file, created_at, user)   # generowany async
```

Reguły:
- Każdy zasób należy do `user` (izolacja danych — filtrowanie po `request.user`).
- `Transaction.amount` > 0, `type` zgodny z `category.type`.
- `Budget` unikalny per (user, category, month, year).

---

## 5. Architektura warstwowa (spełnia kryterium 4.0)

```
apps/
  accounts/        # rejestracja, JWT, profil
  finance/
    models.py      # encje + Manager (warstwa "Repository")
    serializers.py # DTO + walidacja
    services.py    # logika biznesowa (warstwa Service)
    views.py       # ViewSet/APIView (warstwa Controller)
    signals.py     # events domenowe
    tasks.py       # zadania Celery
    selectors.py   # zapytania odczytu (opcjonalnie)
config/
  settings/        # base / dev / prod
  celery.py
```

Zasada: **Views cienkie, logika w services**. ViewSet wywołuje funkcje z `services.py`, te operują na modelach.

---

## 6. Plan implementacji — ETAPY

### ETAP 0 — Setup środowiska (fundament)
- [ ] Repozytorium Git + `.gitignore`, `.env.example`
- [ ] Wirtualne środowisko / `requirements.txt`
- [ ] Projekt Django + DRF, podział `settings` (base/dev/prod)
- [ ] Docker Compose: `web`, `db (postgres)`, `redis`, `worker`
- [ ] README z instrukcją uruchomienia

### ETAP 1 — Działający Django + baza (→ ocena 3.0)
- [ ] Połączenie z PostgreSQL, migracje działają
- [ ] Health-check endpoint `/api/health/`
- [ ] Panel admina dostępny
- **Kryterium spełnione:** Działający backend + połączenie z bazą

### ETAP 2 — CRUD encji (→ ocena 3.0)
- [ ] Model `Transaction` + migracja
- [ ] `TransactionSerializer`
- [ ] `TransactionViewSet` (list/create/retrieve/update/destroy)
- [ ] Routing przez DRF `router`
- [ ] Ręczny test endpointów (Postman / `httpie`)
- **Kryterium spełnione:** CRUD dla 1 encji
- **➡️ Po tym etapie projekt zasługuje na 3.0**

### ETAP 3 — Struktura warstwowa + DTO + walidacja + błędy (→ ocena 4.0)
- [ ] Wydzielenie `services.py` (logika tworzenia/edycji transakcji)
- [ ] Model `Manager`/`selectors` jako warstwa dostępu do danych
- [ ] Serializery jako DTO + walidacja (`amount > 0`, zgodność typu z kategorią)
- [ ] Custom `exception_handler` — jednolity format błędów JSON
- [ ] Walidacja danych wejściowych na wszystkich endpointach
- **Kryterium spełnione:** struktura warstwowa, DTO+walidacja, obsługa błędów

### ETAP 4 — Security / JWT (→ ocena 4.0)
- [ ] `simplejwt`: `/api/auth/login/`, `/api/auth/refresh/`
- [ ] Rejestracja użytkownika `/api/auth/register/`
- [ ] `IsAuthenticated` + izolacja danych per użytkownik
- [ ] Ochrona wszystkich zasobów finansowych
- **Kryterium spełnione:** Security (JWT)
- **➡️ Po tym etapie projekt zasługuje na 4.0**

### ETAP 5 — Pełna domena (funkcje aplikacji)
- [ ] Encje `Category`, `Budget` + CRUD
- [ ] Endpointy analityczne dla dashboardu:
  - `/api/stats/summary/` (przychody vs wydatki)
  - `/api/stats/by-category/` (dane pod wykres kołowy)
  - `/api/stats/monthly/` (trend miesięczny)
- [ ] Logika budżetów miesięcznych (% wykorzystania)
- **Cel:** dane gotowe pod wykresy Chart.js

### ETAP 6 — Kolejki / background jobs (→ ocena 5.0)
- [ ] Celery + Redis skonfigurowane i działające
- [ ] Task: generowanie **raportu CSV** (async)
- [ ] Task: generowanie **raportu PDF** (async)
- [ ] Task: **analiza AI wydatków** (async, z fallbackiem bez klucza API)
- [ ] Model `Report` + endpoint statusu/pobierania pliku
- **Kryterium spełnione:** Kolejki (Celery/Redis)

### ETAP 7 — Events (domknięcie kryterium „Events LUB Kolejki”)
- [ ] Django signals: np. po utworzeniu transakcji → przeliczenie wykorzystania budżetu
- [ ] (opcjonalnie) signal → powiadomienie o przekroczeniu budżetu
- **Kryterium spełnione (nadmiarowo):** Events + Kolejki jednocześnie

### ETAP 8 — Testy jednostkowe (→ ocena 5.0)
- [ ] `pytest-django` skonfigurowany
- [ ] Testy serwisów (logika biznesowa)
- [ ] Testy API (auth, CRUD, walidacja, izolacja danych)
- [ ] Testy walidacji serializerów
- [ ] Coverage raport
- **Kryterium spełnione:** Unit testy

### ETAP 9 — Czysty kod (→ ocena 5.0)
- [ ] `black`, `isort`, `ruff` + konfiguracja
- [ ] `pre-commit` hooki
- [ ] Type hints w services/selectors
- [ ] Usunięcie martwego kodu, spójne nazewnictwo
- **Kryterium spełnione:** czysty kod

### ETAP 10 — Frontend React (→ ocena 5.0)
- [ ] Projekt React (Vite) + Axios (interceptor JWT)
- [ ] Ekran logowania/rejestracji
- [ ] Lista + dodawanie/edycja transakcji (CRUD z UI)
- [ ] Dashboard z wykresami (Chart.js): kołowy wg kategorii + trend miesięczny
- [ ] Widok budżetów
- [ ] Przycisk eksportu PDF/CSV (pobranie wygenerowanego raportu)
- **Kryterium spełnione:** Frontend konsumujący API
- **➡️ Po tym etapie projekt zasługuje na 5.0**

### ETAP 11 — Demo video + dokumentacja
- [ ] README: architektura, uruchomienie, opis API
- [ ] (opcjonalnie) Swagger/OpenAPI (`drf-spectacular`)
- [ ] Nagranie demo: login → CRUD → dashboard → eksport → AI
- **Kryterium spełnione:** Demo video

### ETAP 12 — (Opcjonalnie) Stripe
- [ ] Integracja płatności (np. plan premium / dotacja)
- [ ] Webhook obsługujący zdarzenia Stripe

---

## 7. Mapa: etap → ocena

| Ocena | Etapy wymagane              |
|-------|-----------------------------|
| 3.0   | 0, 1, 2                      |
| 4.0   | + 3, 4                       |
| 5.0   | + 5, 6, 7, 8, 9, 10, 11      |

---

## 8. Sugerowana kolejność pracy (kamienie milowe)

1. **MVP 3.0** — Etapy 0–2 (backend + 1 CRUD)
2. **Solidne 4.0** — Etapy 3–4 (warstwy, walidacja, JWT)
3. **Domena** — Etap 5 (kategorie, budżety, statystyki)
4. **Async 5.0** — Etapy 6–7 (Celery + events + eksport + AI)
5. **Jakość** — Etapy 8–9 (testy + clean code)
6. **Frontend + demo** — Etapy 10–11

---

## 9. Lista zależności (backend `requirements.txt`)

```
Django
djangorestframework
djangorestframework-simplejwt
psycopg2-binary
django-environ
celery
redis
weasyprint            # lub reportlab
drf-spectacular       # dokumentacja API (opcjonalnie)
pytest-django
black
isort
ruff
pre-commit
# anthropic / openai  # analiza AI (opcjonalnie)
# stripe              # płatności (opcjonalnie)
```

Frontend: `react`, `react-dom`, `vite`, `axios`, `chart.js`, `react-chartjs-2`, `react-router-dom`.
