
import React from "react";
import StockSearch from "../components/StockSearch";

const ForecastPage: React.FC = () => {
  return (
    <>
      <h1 className="text-2xl font-bold mb-4">Forecast & News</h1>
      <StockSearch />
    </>
  );
};

export default ForecastPage;