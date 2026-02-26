import React from "react";
import { NavLink } from "react-router-dom";

const SideNav: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r p-4">
      <h2 className="text-xl font-bold mb-6">📈 Stock Predictor</h2>

      <nav className="flex flex-col gap-2">
        <NavLink
          to="/live"
          className={({ isActive }) =>
            `p-2 rounded ${
              isActive ? "bg-blue-100 font-semibold" : "hover:bg-gray-100"
            }`
          }
        >
          Live Market
        </NavLink>
        <NavLink
          to="/forecasting"
          className={({ isActive }) =>
            `p-2 rounded ${
              isActive ? "bg-blue-100 font-semibold" : "hover:bg-gray-100"
            }`
          }
        >
          Forecasting
        </NavLink>
        <NavLink
          to="/forecast"
          className={({ isActive }) =>
            `p-2 rounded ${
              isActive ? "bg-blue-100 font-semibold" : "hover:bg-gray-100"
            }`
          }
        >
          Forecast Analysis
        </NavLink>
        <NavLink
          to="/historicaldata"
          className={({ isActive }) =>
            `p-2 rounded ${
              isActive ? "bg-blue-100 font-semibold" : "hover:bg-gray-100"
            }`
          }
        >
          Fetch Historical Data
        </NavLink>
      </nav>
    </aside>
  );
};

export default SideNav;