import React from "react";
import ReviewAnalyzer from "./components/ReviewAnalyzer";

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center mb-6">📊 Product Sentiment Analyzer</h1>
      <ReviewAnalyzer />
    </div>
  );
}

export default App;