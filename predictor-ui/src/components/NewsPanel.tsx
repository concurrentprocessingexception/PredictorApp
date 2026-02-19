import React, { useEffect, useState } from 'react';
import { fetchNews } from '../services/newsService';

type Props = {
  searchSymbol: string;
};

const sentimentColorMap: Record<string, string> = {
  Positive: 'text-green-600',
  Negative: 'text-red-600',
  Neutral: 'text-yellow-600',
};

const NewsPanel: React.FC<Props> = ({ searchSymbol }) => {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadNews = async () => {
      setLoading(true);
      const results = await fetchNews(searchSymbol);
      setArticles(results);
      setLoading(false);
    };

    if (searchSymbol) {
      loadNews();
    }
  }, [searchSymbol]);

  return (
    <div className="p-4 border rounded shadow h-full">
      <h2 className="text-lg font-semibold mb-2">📰 News & Sentiment</h2>

      {loading && <p className="text-sm text-gray-500">Loading news...</p>}

      {!loading && articles.length > 0 && (
        <ul className="space-y-2">
          {articles.slice(0, 10).map((article, idx) => (
            <li key={idx} className="border p-2 rounded">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-blue-700 hover:underline"
              >
                {article.headline}
              </a>
              <div className="text-sm text-gray-600">
                {article.datetime &&
                  new Date(article.datetime * 1000).toLocaleString()}
              </div>
              <div className="text-sm italic mt-1">
                Sentiment:{' '}
                <span
                  className={`font-bold ${
                    sentimentColorMap[article.sentiment] ?? 'text-gray-500'
                  }`}
                >
                  {article.sentiment}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}

      {!loading && articles.length === 0 && (
        <p className="text-sm text-gray-500">No news found.</p>
      )}
    </div>
  );
};

export default NewsPanel;
