import React, { useEffect, useState } from 'react';
import { fetchNews } from '../services/newsService';

type Props = {
  searchSymbol: string;
};

type Sentiment = 'Positive' | 'Neutral' | 'Negative';

const sentimentColorMap: Record<Sentiment, string> = {
  Positive: 'text-green-600',
  Neutral: 'text-yellow-600',
  Negative: 'text-red-600',
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

  const groupedNews: Record<Sentiment, any[]> = {
    Positive: articles.filter(a => a.sentiment === 'Positive'),
    Neutral: articles.filter(a => a.sentiment === 'Neutral'),
    Negative: articles.filter(a => a.sentiment === 'Negative'),
  };

  return (
    <div className="p-4 border rounded shadow">
      <h2 className="text-lg font-semibold mb-4">
        📰 News & Sentiment
      </h2>

      {loading && (
        <p className="text-sm text-gray-500">Loading news...</p>
      )}

      {!loading && articles.length === 0 && (
        <p className="text-sm text-gray-500">No news found.</p>
      )}

      {!loading && articles.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                {(['Positive', 'Neutral', 'Negative'] as Sentiment[]).map(
                  sentiment => (
                    <th
                      key={sentiment}
                      className={`border p-2 text-center font-semibold ${sentimentColorMap[sentiment]}`}
                    >
                      {sentiment}
                    </th>
                  )
                )}
              </tr>
            </thead>

            <tbody>
              <tr>
                {(['Positive', 'Neutral', 'Negative'] as Sentiment[]).map(
                  sentiment => (
                    <td
                      key={sentiment}
                      className="border p-2 align-top w-1/3"
                    >
                      <ul className="space-y-2">
                        {groupedNews[sentiment]
                          .slice(0, 10)
                          .map((article, idx) => (
                            <li key={idx} className="text-sm">
                              <a
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-700 hover:underline font-medium"
                              >
                                {article.headline}
                              </a>
                              <div className="text-xs text-gray-500">
                                {article.datetime &&
                                  new Date(
                                    article.datetime * 1000
                                  ).toLocaleString()}
                              </div>
                            </li>
                          ))}

                        {groupedNews[sentiment].length === 0 && (
                          <li className="text-xs text-gray-400 italic">
                            No articles
                          </li>
                        )}
                      </ul>
                    </td>
                  )
                )}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default NewsPanel;