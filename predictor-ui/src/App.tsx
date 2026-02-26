import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./layout/AppLayout";
import HistoricalDataPage from "./pages/DataPage";
import ForecastPage from "./pages/ForecastPage";
import LivePage from "./pages/Live";
import InitiateForecastPage from "./pages/InitiateForecastPage";

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/live" />} />
          <Route path="historicaldata" element={<HistoricalDataPage />} />
          <Route path="live" element={<LivePage />} />
          <Route path="forecast" element={<ForecastPage />} />
          <Route path="forecasting" element={<InitiateForecastPage />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;