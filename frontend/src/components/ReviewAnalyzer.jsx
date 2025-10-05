// frontend/src/components/ReviewAnalyzer.jsx

import React, { useState, useMemo } from "react";
import axios from "axios";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LabelList,
} from "recharts";

const COLOR_MAP = {
  "Positive 📈": "#22c55e", // green
  "Neutral ⚖️": "#eab308",  // yellow
  "Negative 📉": "#ef4444", // red
};

export default function ReviewAnalyzer() {
  const [product, setProduct] = useState("");
  const [source, setSource] = useState("both");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchReviews = async () => {
    if (!product.trim()) return;
    setLoading(true);
    try {
      const res = await axios.get("http://127.0.0.1:5000/api/reviews", {
        params: { product, source },
      });
      setResult(res.data);
    } catch (err) {
      console.error("Error fetching reviews:", err);
      setResult(null);
    }
    setLoading(false);
  };

  const reviews = useMemo(() => (result ? result.reviews || [] : []), [result]);

  const counts = useMemo(() => {
    return {
      positive: reviews.filter((r) => r.sentiment === "positive").length,
      neutral: reviews.filter((r) => r.sentiment === "neutral").length,
      negative: reviews.filter((r) => r.sentiment === "negative").length,
    };
  }, [reviews]);

  const total = reviews.length || 1;

  const chartData = useMemo(
    () => [
      {
        name: "Positive 📈",
        value: counts.positive,
        percent: (counts.positive / total) * 100,
      },
      {
        name: "Neutral ⚖️",
        value: counts.neutral,
        percent: (counts.neutral / total) * 100,
      },
      {
        name: "Negative 📉",
        value: counts.negative,
        percent: (counts.negative / total) * 100,
      },
    ],
    [counts, total]
  );

  const wordFreq = useMemo(() => {
    const freq = {};
    const stopwords = new Set([
      "the","is","and","to","it","in","for","of","this","that","with",
      "on","as","but","so","are","be","or","if","an","a"
    ]);
    reviews.forEach((r) => {
      r.review
        .toLowerCase()
        .split(/\W+/)
        .forEach((word) => {
          if (word && !stopwords.has(word)) {
            freq[word] = (freq[word] || 0) + 1;
          }
        });
    });

    const totalWords = Object.values(freq).reduce((a, b) => a + b, 0) || 1;
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 7)
      .map(([word, count]) => ({
        word,
        count,
        percent: ((count / totalWords) * 100).toFixed(1),
      }));
  }, [reviews]);

  const getInsights = () => {
    if (counts.positive > counts.negative && counts.positive > counts.neutral) {
      return "✅ The majority of reviews are positive. Customers are satisfied.";
    } else if (counts.negative > counts.positive) {
      return "⚠️ Many customers expressed negative feedback. Improvements may be needed.";
    } else {
      return "ℹ️ Reviews are mostly neutral. Customers have mixed opinions.";
    }
  };

  const renderReviews = (title, emoji, sentiment, colorClass) => {
    const filtered = reviews.filter((r) => r.sentiment === sentiment);
    if (!filtered.length) return null;

    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <span className={colorClass}>{emoji}</span> {title} Reviews ({filtered.length})
        </h3>
        <ul className="space-y-3">
          {filtered.map((r, i) => (
            <li key={i} className="border p-3 rounded-lg shadow-sm bg-gray-50">
              <p className="text-sm">{r.review}</p>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="bg-white shadow rounded-2xl p-6 max-w-6xl mx-auto">
      {/* Search Bar */}
      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <input
          type="text"
          placeholder="🔍 Enter product name..."
          value={product}
          onChange={(e) => setProduct(e.target.value)}
          className="flex-1 border p-2 rounded-lg"
        />
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          className="border p-2 rounded-lg"
        >
          <option value="amazon">Amazon</option>
          <option value="flipkart">Flipkart</option>
          <option value="both">Both</option>
        </select>
        <button
          onClick={fetchReviews}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Analyze 📊
        </button>
      </div>

      {loading && <p className="text-center text-lg">⏳ Fetching reviews...</p>}

      {!loading && reviews.length > 0 && (
        <div className="space-y-12">
          {/* ✅ Sentiment Summary Table */}
          <div className="bg-gray-100 rounded-lg p-5 shadow">
            <h2 className="text-2xl font-semibold mb-4 text-center">📊 Sentiment Summary</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-center">
                <thead>
                  <tr className="bg-gray-200">
                    <th className="border p-2">Sentiment</th>
                    <th className="border p-2">Reviews</th>
                    <th className="border p-2">Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {chartData.map((row, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="border p-2">{row.name}</td>
                      <td className="border p-2">{row.value}</td>
                      <td className="border p-2">{row.percent.toFixed(2)}%</td>
                    </tr>
                  ))}
                  <tr className="font-bold bg-gray-200">
                    <td className="border p-2">Total</td>
                    <td className="border p-2">{reviews.length}</td>
                    <td className="border p-2">100.00%</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="mt-3 italic text-gray-700 text-center">{getInsights()}</p>
          </div>

          {/* ✅ Pie Chart */}
          <div className="flex flex-col items-center space-y-4">
            <h2 className="text-xl font-semibold">📊 Sentiment Overview</h2>
            <PieChart width={420} height={350}>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={120}
                label={({ name }) => {
                  const item = chartData.find((d) => d.name === name);
                  return `${item.percent.toFixed(2)}%`;
                }}
                labelLine={false}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLOR_MAP[entry.name]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(val, name) => {
                  const item = chartData.find((d) => d.name === name);
                  return [`${val} reviews (${item.percent.toFixed(2)}%)`, name];
                }}
              />
              <Legend
                formatter={(value) => {
                  const item = chartData.find((d) => d.name === value);
                  return `${value}: ${item.value} (${item.percent.toFixed(2)}%)`;
                }}
              />
            </PieChart>
          </div>

          {/* ✅ Word Frequency */}
          {wordFreq.length > 0 && (
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-4">📑 Key Terms in Reviews</h2>
              <BarChart width={650} height={320} data={wordFreq} className="mx-auto">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="word" />
                <YAxis />
                <Tooltip
                  formatter={(val, name, props) => [
                    `${val} (${props.payload.percent}%)`,
                    "Mentions",
                  ]}
                />
                <Bar dataKey="count" fill="#3b82f6">
                  <LabelList
                    dataKey="percent"
                    position="top"
                    formatter={(val) => `${val}%`}
                    fill="#111"
                  />
                </Bar>
              </BarChart>
            </div>
          )}

          {/* ✅ Grouped Reviews */}
          <div>
            {renderReviews("Positive", "📈", "positive", "text-green-600")}
            {renderReviews("Negative", "📉", "negative", "text-red-600")}
            {renderReviews("Neutral", "⚖️", "neutral", "text-yellow-600")}
          </div>
        </div>
      )}
    </div>
  );
}
