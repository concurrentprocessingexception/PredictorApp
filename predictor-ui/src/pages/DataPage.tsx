import React from "react";
import UploadPanel from "../components/UploadPanel";

const HistoricalDataPage: React.FC = () => {
  return (
    <>
      <h1 className="text-2xl font-bold mb-4">Fetch Historical Data</h1>
      <UploadPanel />
    </>
  );
};

export default HistoricalDataPage;