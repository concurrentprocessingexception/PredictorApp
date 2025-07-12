import React from 'react';
import StockSearch from './components/StockSearch';

const App: React.FC = () => {
  return (
    <div className="w-full mx-auto mt-10 px-4">
      <h1 className="text-2xl font-bold mb-6 text-center">📈 Stock Predictor UI</h1>
      <StockSearch />
    </div>
  );
};

export default App;
