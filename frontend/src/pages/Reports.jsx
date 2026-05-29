import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";

const TYPE_LABELS = { CSV: "Eksport CSV", PDF: "Raport PDF", AI: "Analiza AI" };
const STATUS_LABELS = {
  PENDING: "Oczekuje",
  PROCESSING: "W trakcie",
  DONE: "Gotowe",
  FAILED: "Blad",
};

export default function Reports() {
  const now = new Date();
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    type: "CSV",
    month: now.getMonth() + 1,
    year: now.getFullYear(),
  });
  const timer = useRef(null);

  const load = () => api.get("/reports/").then((r) => setItems(r.data.results));

  useEffect(() => {
    load();
    return () => clearInterval(timer.current);
  }, []);

  // Auto-odswiezanie dopoki jakis raport jest w trakcie (kolejka Celery)
  useEffect(() => {
    const pending = items.some(
      (r) => r.status === "PENDING" || r.status === "PROCESSING",
    );
    clearInterval(timer.current);
    if (pending) timer.current = setInterval(load, 1500);
    return () => clearInterval(timer.current);
  }, [items]);

  const generate = async (e) => {
    e.preventDefault();
    await api.post("/reports/", form);
    load();
  };

  const download = async (r) => {
    const res = await api.get(`/reports/${r.id}/download/`, {
      responseType: "blob",
    });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `raport_${r.id}.${r.type.toLowerCase()}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <h2>Raporty i analiza</h2>

      <form className="card row-form" onSubmit={generate}>
        <select
          value={form.type}
          onChange={(e) => setForm({ ...form, type: e.target.value })}
        >
          <option value="CSV">Eksport CSV</option>
          <option value="PDF">Raport PDF</option>
          <option value="AI">Analiza AI</option>
        </select>
        <input
          type="number"
          min="1"
          max="12"
          value={form.month}
          onChange={(e) => setForm({ ...form, month: e.target.value })}
        />
        <input
          type="number"
          value={form.year}
          onChange={(e) => setForm({ ...form, year: e.target.value })}
        />
        <button type="submit">Generuj</button>
      </form>
      <p className="muted">
        Raporty generowane są asynchronicznie (kolejka Celery) — status
        odświeża się automatycznie.
      </p>

      <table className="card table">
        <thead>
          <tr>
            <th>Typ</th>
            <th>Okres</th>
            <th>Status</th>
            <th>Wynik</th>
          </tr>
        </thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.id}>
              <td>{TYPE_LABELS[r.type] || r.type}</td>
              <td>
                {r.month}/{r.year}
              </td>
              <td>
                <span className={`badge badge-${r.status.toLowerCase()}`}>
                  {STATUS_LABELS[r.status] || r.status}
                </span>
              </td>
              <td>
                {r.status === "DONE" && r.type !== "AI" && (
                  <button className="link-btn" onClick={() => download(r)}>
                    Pobierz
                  </button>
                )}
                {r.status === "DONE" && r.type === "AI" && (
                  <pre className="ai-result">{r.result}</pre>
                )}
                {r.status === "FAILED" && (
                  <span className="neg">{r.error}</span>
                )}
                {(r.status === "PENDING" || r.status === "PROCESSING") && (
                  <span className="muted">…</span>
                )}
              </td>
            </tr>
          ))}
          {!items.length && (
            <tr>
              <td colSpan="4" className="muted">
                Brak raportów — wygeneruj pierwszy powyżej.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
