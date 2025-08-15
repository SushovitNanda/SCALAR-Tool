
import { toast } from "sonner";

export interface ClassDescription {
  name: string;
  description: string;
}

export interface AnalysisParameters {
  embedding_type: "sentence-bert" | "sentence-roberta";
  clustering_method: "kmeans" | "hac" | "gmm" | "birch";
  num_clusters: number;
  min_wiki_pages: number;
  use_bertopic: boolean;
  class_descriptions: Record<string, string>;
}

export interface AnalysisResults {
  parameters: AnalysisParameters;
  raw_embeddings: {
    document_embeddings: number[][];
    label_embeddings: number[][];
    embedding_dimension: number;
  };
  domain_corpus: Record<string, {
    source: 'user_uploaded' | 'wikipedia_extracted';
    search_terms?: string;
    text: string;
  }>;
  cluster_distribution: Record<string, { count: number; percentage: number }>;
  visualizations: {
    cluster_viz?: string;
    similarity_matrix?: string;
    cluster_sizes?: string;
  };
  bertopic_results?: {
    topic_reports: Array<{
      cluster_id: number;
      cluster_label: string;
      topic_id: number;
      top_terms: string;
      term_scores: Record<string, number>;
      sample_count: number;
    }>;
    topic_summaries: Record<string, string[]>;
  };
}

const BASE_URL = "http://localhost:5000";

export const uploadFile = async (file: File): Promise<{ success: boolean; filename?: string }> => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Upload failed");
    }

    return await response.json();
  } catch (error) {
    console.error("Upload error:", error);
    throw error;
  }
};

export const setParameters = async (params: AnalysisParameters): Promise<{ success: boolean }> => {
  try {
    const response = await fetch(`${BASE_URL}/set-parameters`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to set parameters");
    }

    return await response.json();
  } catch (error) {
    console.error("Parameters error:", error);
    throw error;
  }
};

export const runAnalysis = async (): Promise<{ success: boolean; message?: string }> => {
  try {
    const response = await fetch(`${BASE_URL}/run-analysis`, {
      method: "POST",
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Analysis failed");
    }

    return await response.json();
  } catch (error) {
    console.error("Analysis error:", error);
    throw error;
  }
};

export const getResults = async (): Promise<{ success: boolean; results?: AnalysisResults }> => {
  try {
    const response = await fetch(`${BASE_URL}/results`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to fetch results");
    }

    return await response.json();
  } catch (error) {
    console.error("Results error:", error);
    throw error;
  }
};

export const downloadResults = (format: 'csv' | 'json') => {
  const url = `${BASE_URL}/download-${format}`;
  window.open(url, '_blank');
};

