import { useEffect, useState } from "react";
import { api } from "../api/client";

const EMPTY = {
  type: "EXPENSE",
  amount: "",
  category: "",
  description: "",
  date: new Date().toISOString().slice(0, 10),
};

export default function Transactions() {
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [newCat, setNewCat] = useState("");
  const randomColor = () =>
    "#" +
    Math.floor(Math.random() * 0xffffff)
      .toString(16)
      .padStart(6, "0");
  const [newCatColor, setNewCatColor] = useState(randomColor);
  const [error, setError] = useState("");

  const load = () => {
    api.get("/transactions/").then((r) => setItems(r.data.results));
    api.get("/categories/").then((r) => setCategories(r.data.results));
  };
  useEffect(load, []);

  const addTransaction = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const payload = { ...form, category: form.category || null };
      await api.post("/transactions/", payload);
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(JSON.stringify(err.response?.data?.error?.detail || "Blad"));
    }
  };

  const addCategory = async () => {
    if (!newCat) return;
    await api.post("/categories/", {
      name: newCat,
      type: form.type,
      color: newCatColor,
    });
    setNewCat("");
    setNewCatColor(randomColor());
    load();
  };

  const remove = async (id) => {
    await api.delete(`/transactions/${id}/`);
    load();
  };

  return (
    <div>
      <h2>Transakcje</h2>

      <form className="card row-form" onSubmit={addTransaction}>
        <select
          value={form.type}
          onChange={(e) => setForm({ ...form, type: e.target.value })}
        >
          <option value="EXPENSE">Wydatek</option>
          <option value="INCOME">Przychod</option>
        </select>
        <input
          type="number"
          step="0.01"
          placeholder="Kwota"
          value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
        />
        <select
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
        >
          <option value="">— kategoria —</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          placeholder="Opis"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <input
          type="date"
          value={form.date}
          onChange={(e) => setForm({ ...form, date: e.target.value })}
        />
        <button type="submit">Dodaj</button>
      </form>
      {error && <p className="error">{error}</p>}

      <div className="card row-form">
        <input
          placeholder="Nowa kategoria"
          value={newCat}
          onChange={(e) => setNewCat(e.target.value)}
        />
        <input
          type="color"
          title="Kolor kategorii"
          value={newCatColor}
          onChange={(e) => setNewCatColor(e.target.value)}
        />
        <button type="button" onClick={addCategory}>
          Dodaj kategorie ({form.type})
        </button>
      </div>

      <table className="card table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Typ</th>
            <th>Kategoria</th>
            <th>Opis</th>
            <th>Kwota</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((t) => (
            <tr key={t.id}>
              <td>{t.date}</td>
              <td>{t.type === "INCOME" ? "Przychod" : "Wydatek"}</td>
              <td>{t.category_name || "—"}</td>
              <td>{t.description}</td>
              <td className={t.type === "INCOME" ? "pos" : "neg"}>
                {t.amount}
              </td>
              <td>
                <button className="link" onClick={() => remove(t.id)}>
                  usun
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
