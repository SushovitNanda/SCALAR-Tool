import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { getResults, downloadResults, AnalysisResults } from "@/services/analysisService";

export default function ResultsDisplay() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getResults();
      if (response.success && response.results) {
        setResults(response.results);
      } else {
        throw new Error("Failed to fetch results");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to load results");
      toast.error(error instanceof Error ? error.message : "Failed to load results");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  if (loading) {
    return (
      <Card className="p-6 text-center">
        <div className="space-y-4">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto"></div>
          <p>Analysis in progress... This may take several minutes.</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center space-y-4">
          <p className="text-red-500">{error}</p>
          <div className="space-x-4">
            <Button variant="outline" onClick={fetchResults}>
              Retry
            </Button>
            <Button variant="outline" onClick={() => navigate("/parameters")}>
              Back to Parameters
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  if (!results) {
    return (
      <Card className="p-6 text-center">
        <p>No results available</p>
        <Button variant="outline" onClick={() => navigate("/parameters")}>
          Back to Parameters
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Cluster Distribution</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Label</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Count</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Percentage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {Object.entries(results.cluster_distribution).map(([label, data]) => (
                <tr key={label}>
                  <td className="px-6 py-4 whitespace-nowrap">{label}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{data.count}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{(data.percentage * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Visualizations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.visualizations.cluster_viz && (
            <div>
              <h4 className="text-sm font-medium mb-2">Document Clusters</h4>
              <img 
                src={`data:image/png;base64,${results.visualizations.cluster_viz}`} 
                alt="Cluster Visualization"
                className="w-full rounded"
              />
            </div>
          )}
          {results.visualizations.similarity_matrix && (
            <div>
              <h4 className="text-sm font-medium mb-2">Similarity Matrix</h4>
              <img 
                src={`data:image/png;base64,${results.visualizations.similarity_matrix}`} 
                alt="Similarity Matrix"
                className="w-full rounded"
              />
            </div>
          )}
          {results.visualizations.cluster_sizes && (
            <div>
              <h4 className="text-sm font-medium mb-2">Cluster Sizes</h4>
              <img 
                src={`data:image/png;base64,${results.visualizations.cluster_sizes}`} 
                alt="Cluster Sizes"
                className="w-full rounded"
              />
            </div>
          )}
        </div>
      </Card>

      {results.bertopic_results && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Topic Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(results.bertopic_results.topic_summaries).map(([clusterId, summaries]) => (
              <Card key={clusterId} className="p-4">
                <h4 className="font-medium mb-2">Cluster {clusterId}</h4>
                <ul className="list-disc list-inside space-y-1">
                  {summaries.map((summary, idx) => (
                    <li key={idx} className="text-sm">{summary}</li>
                  ))}
                </ul>
              </Card>
            ))}
          </div>
        </Card>
      )}

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Download Results</h3>
        <div className="flex space-x-4">
          <Button onClick={() => downloadResults('csv')}>
            Download SCALAR Results (CSV)
          </Button>
          <Button variant="outline" onClick={() => downloadResults('json')}>
            Download SCALAR Results (JSON)
          </Button>
        </div>
      </Card>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => navigate("/parameters")}>
          Back to Parameters
        </Button>
        <Button onClick={() => navigate("/")}>
          New Analysis
        </Button>
      </div>
    </div>
  );
}
