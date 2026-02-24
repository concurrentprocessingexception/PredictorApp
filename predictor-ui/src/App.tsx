import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./layout/AppLayout";
import DataPage from "./pages/DataPage";
import ForecastPage from "./pages/ForecastPage";

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/forecast" />} />
          <Route path="data" element={<DataPage />} />
          <Route path="forecast" element={<ForecastPage />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;