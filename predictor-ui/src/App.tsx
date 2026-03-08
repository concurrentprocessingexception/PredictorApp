import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./layout/AppLayout";
import HistoricalDataPage from "./pages/DataPage";
import ForecastPage from "./pages/ForecastPage";
import LivePage from "./pages/Live";
import InitiateForecastPage from "./pages/InitiateForecastPage";
import ForecastHistoryPage from "./pages/ForecastHistoryPage";

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/live" />} />
          <Route path="live" element={<LivePage />} />
          <Route path="forecasting" element={<InitiateForecastPage />} />
          <Route path="forecast" element={<ForecastPage />} />
          <Route path="forecasthistory" element={<ForecastHistoryPage />} />
          <Route path="historicaldata" element={<HistoricalDataPage />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;