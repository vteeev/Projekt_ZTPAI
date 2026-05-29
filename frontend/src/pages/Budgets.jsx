import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Budgets() {
  const now = new Date();
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    category: "",
    month: now.getMonth() + 1,
    year: now.getFullYear(),
    amount: "",
  });

  const load = () => {
    api.get("/budgets/").then((r) => setItems(r.data.results));
    api.get("/categories/").then((r) => setCategories(r.data.results));
  };
  useEffect(load, []);

  const add = async (e) => {
    e.preventDefault();
    await api.post("/budgets/", {
      ...form,
      category: form.category || null,
    });
    setForm({ ...form, amount: "" });
    load();
  };

  const catName = (id) =>
    categories.find((c) => c.id === id)?.name || "Laczny";

  return (
    <div>
      <h2>Budzety miesieczne</h2>

      <form className="card row-form" onSubmit={add}>
        <select
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
        >
          <option value="">— laczny —</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
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
        <input
          type="number"
          step="0.01"
          placeholder="Limit"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
        />
        <button type="submit">Dodaj budzet</button>
      </form>

      <div className="budgets">
        {items.map((b) => (
          <div className="card budget" key={b.id}>
            <div className="budget-head">
              <strong>{catName(b.category)}</strong>
              <span>
                {b.month}/{b.year}
              </span>
            </div>
            <div className="progress">
              <div
                className="progress-bar"
                style={{
                  width: `${Math.min(b.usage_percent, 100)}%`,
                  background: b.usage_percent > 100 ? "#ef4444" : "#3b82f6",
                }}
              />
            </div>
            <div className="budget-foot">
              <span>
                {b.spent} / {b.amount} PLN
              </span>
              <span className={b.usage_percent > 100 ? "neg" : ""}>
                {b.usage_percent}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
