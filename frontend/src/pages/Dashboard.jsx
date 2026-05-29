import { useEffect, useState } from "react";
import { Doughnut, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { api } from "../api/client";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
);

const MONTHS = [
  "Sty", "Lut", "Mar", "Kwi", "Maj", "Cze",
  "Lip", "Sie", "Wrz", "Paz", "Lis", "Gru",
];

// Generuje rozlozone kolory na kole barw (gdy kategorie nie maja wlasnego koloru
// lub kolory sie powtarzaja - kazdy wycinek dostaje inny kolor).
function distinctColors(items) {
  const used = new Set();
  return items.map((c, i) => {
    let color = c.color;
    if (!color || used.has(color)) {
      const hue = Math.round((360 * i) / Math.max(items.length, 1));
      color = `hsl(${hue}, 65%, 55%)`;
    }
    used.add(color);
    return color;
  });
}

export default function Dashboard() {
  const now = new Date();
  const [summary, setSummary] = useState(null);
  const [byCat, setByCat] = useState([]);
  const [monthly, setMonthly] = useState([]);

  useEffect(() => {
    const m = now.getMonth() + 1;
    const y = now.getFullYear();
    api.get(`/stats/summary/?month=${m}&year=${y}`).then((r) => setSummary(r.data));
    api.get(`/stats/by-category/?month=${m}&year=${y}`).then((r) => setByCat(r.data));
    api.get(`/stats/monthly/?year=${y}`).then((r) => setMonthly(r.data));
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="cards">
        <div className="card stat income">
          <span>Przychody</span>
          <strong>{summary?.income ?? 0} PLN</strong>
        </div>
        <div className="card stat expense">
          <span>Wydatki</span>
          <strong>{summary?.expense ?? 0} PLN</strong>
        </div>
        <div className="card stat balance">
          <span>Bilans</span>
          <strong>{summary?.balance ?? 0} PLN</strong>
        </div>
      </div>

      <div className="charts">
        <div className="card chart">
          <h3>Wydatki wg kategorii</h3>
          {byCat.length ? (
            <Doughnut
              data={{
                labels: byCat.map((c) => c.category),
                datasets: [
                  {
                    data: byCat.map((c) => c.total),
                    backgroundColor: distinctColors(byCat),
                  },
                ],
              }}
            />
          ) : (
            <p className="muted">Brak danych.</p>
          )}
        </div>

        <div className="card chart">
          <h3>Trend miesieczny</h3>
          <Bar
            data={{
              labels: monthly.map((m) => MONTHS[m.month - 1]),
              datasets: [
                {
                  label: "Przychody",
                  data: monthly.map((m) => m.income),
                  backgroundColor: "#22c55e",
                },
                {
                  label: "Wydatki",
                  data: monthly.map((m) => m.expense),
                  backgroundColor: "#ef4444",
                },
              ],
            }}
          />
        </div>
      </div>
    </div>
  );
}
