# Scenariusz demo (nagranie wideo)

Poniższy scenariusz pokrywa wszystkie kryteria oceny. Sugerowana długość: 3–5 min.

## Przygotowanie

```bash
# Terminal 1 - backend
cp .env.example .env
docker compose up --build
docker compose exec web python manage.py createsuperuser

# Terminal 2 - frontend
cd frontend && cp .env.example .env && npm install && npm run dev
```

## Przebieg nagrania

1. **Uruchomienie (3.0 — działający backend + baza)**
   - Pokaż `docker compose ps` (web, db, redis, worker działają).
   - Otwórz `http://localhost:8000/api/health/` → `{"status":"ok","database":"connected"}`.

2. **Dokumentacja API (Swagger)**
   - Otwórz `http://localhost:8000/api/docs/` — pokaż listę endpointów.

3. **Rejestracja i logowanie (4.0 — JWT)**
   - W aplikacji React (`http://localhost:5173`) zarejestruj użytkownika.
   - Pokaż, że po zalogowaniu otrzymujesz dostęp (token JWT w localStorage).

4. **CRUD transakcji (3.0 — CRUD)**
   - Dodaj kilka transakcji (przychód + wydatki), utwórz kategorię.
   - Usuń jedną transakcję. Pokaż aktualizację listy.

5. **Walidacja i obsługa błędów (4.0)**
   - Spróbuj dodać transakcję z ujemną kwotą → komunikat błędu.
   - (Opcjonalnie w Swaggerze) pokaż jednolity format `{"error": {...}}`.

6. **Dashboard / analityka (wykresy)**
   - Pokaż dashboard: karty (przychody/wydatki/bilans), wykres kołowy
     wg kategorii i słupkowy trend miesięczny (Chart.js).

7. **Budżety i events (5.0 — signals)**
   - Dodaj budżet na kategorię z niskim limitem.
   - Dodaj wydatek przekraczający limit.
   - Pokaż `GET /api/notifications/` → powiadomienie o przekroczeniu (sygnał).

8. **Kolejki / background jobs (5.0 — Celery)**
   - Zleć raport: `POST /api/reports/` (CSV / PDF / AI).
   - Pokaż logi workera (`docker compose logs worker`) — zadanie przetworzone.
   - Pobierz plik: `GET /api/reports/{id}/download/`.
   - Pokaż analizę AI (`type=AI`) — tekst rekomendacji.

9. **Izolacja danych (4.0 — security)**
   - Zaloguj drugiego użytkownika — nie widzi danych pierwszego.

10. **Jakość i testy (5.0)**
    - `docker compose exec web pytest` → 19 passed.
    - `docker compose exec web ruff check .` → All checks passed.

## Mapowanie na oceny

- **3.0**: kroki 1, 4
- **4.0**: kroki 3, 5, 9
- **5.0**: kroki 6, 7, 8, 10 + frontend (cały pokaz)
