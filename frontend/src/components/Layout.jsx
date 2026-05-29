import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>💰 Finanse</h1>
        <nav>
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/transactions">Transakcje</NavLink>
          <NavLink to="/budgets">Budzety</NavLink>
        </nav>
        <div className="sidebar-footer">
          <span>{user?.username}</span>
          <button onClick={handleLogout}>Wyloguj</button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
