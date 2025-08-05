import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Input } from "./ui/input";
import { Switch } from "./ui/switch";
import { setParameters, runAnalysis, AnalysisParameters } from "@/services/analysisService";

export default function ParameterForm() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<AnalysisParameters>({
    embedding_type: "sentence-bert",
    clustering_method: "kmeans",
    num_clusters: 2,
    min_wiki_pages: 3,
    use_bertopic: true,
    class_descriptions: {},
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // First, set the parameters
      await setParameters(formData);
      
      // Then run the analysis
      await runAnalysis();
      
      toast.success("Analysis started successfully");
      navigate("/results");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Analysis failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const updateClassDescriptions = useCallback((index: number, field: 'name' | 'description', value: string) => {
    setFormData(prev => {
      const newClassDescs = { ...prev.class_descriptions };
      if (field === 'name') {
        const oldValue = Object.keys(newClassDescs)[index];
        if (oldValue) {
          const desc = newClassDescs[oldValue];
          delete newClassDescs[oldValue];
          newClassDescs[value] = desc;
        } else {
          newClassDescs[value] = '';
        }
      } else {
        const name = Object.keys(newClassDescs)[index] || `Class ${index + 1}`;
        newClassDescs[name] = value;
      }
      return { ...prev, class_descriptions: newClassDescs };
    });
  }, []);

  const classFields = Array.from({ length: formData.num_clusters }, (_, i) => (
    <div key={i} className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor={`class-name-${i}`}>Class {i + 1} Name</Label>
        <Input
          id={`class-name-${i}`}
          placeholder="e.g., Computer Science"
          onChange={(e) => updateClassDescriptions(i, 'name', e.target.value)}
          value={Object.keys(formData.class_descriptions)[i] || ''}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor={`class-desc-${i}`}>Class {i + 1} Description</Label>
        <Input
          id={`class-desc-${i}`}
          placeholder="e.g., Computing theory and applications"
          onChange={(e) => updateClassDescriptions(i, 'description', e.target.value)}
          value={Object.values(formData.class_descriptions)[i] || ''}
        />
      </div>
    </div>
  ));

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card className="p-6 space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="embedding-type">Embedding Type</Label>
            <Select
              value={formData.embedding_type}
              onValueChange={(value: "sentence-bert" | "sentence-roberta") => 
                setFormData(prev => ({ ...prev, embedding_type: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select embedding type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sentence-bert">Sentence BERT</SelectItem>
                <SelectItem value="sentence-roberta">Sentence RoBERTa</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="clustering-method">Clustering Method</Label>
            <Select
              value={formData.clustering_method}
              onValueChange={(value: "kmeans" | "hac" | "gmm" | "birch") => 
                setFormData(prev => ({ ...prev, clustering_method: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select clustering method" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="kmeans">K-Means</SelectItem>
                <SelectItem value="hac">Hierarchical Clustering</SelectItem>
                <SelectItem value="gmm">Gaussian Mixture Model</SelectItem>
                <SelectItem value="birch">BIRCH</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="num-clusters">Number of Classes/Labels</Label>
            <Select
              value={formData.num_clusters.toString()}
              onValueChange={(value) => 
                setFormData(prev => ({ ...prev, num_clusters: parseInt(value) }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select number of clusters" />
              </SelectTrigger>
              <SelectContent>
                {[2, 3, 4, 5].map(num => (
                  <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="min-wiki-pages">Wikipedia Pages Per Term</Label>
            <Input
              type="number"
              min={2}
              max={25}
              value={formData.min_wiki_pages}
              onChange={(e) => 
                setFormData(prev => ({ ...prev, min_wiki_pages: parseInt(e.target.value) }))}
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Switch
            checked={formData.use_bertopic}
            onCheckedChange={(checked) => 
              setFormData(prev => ({ ...prev, use_bertopic: checked }))}
          />
          <Label>Use BERTopic for Post-hoc Analysis</Label>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Class Descriptions</h3>
          {classFields}
        </div>

        <div className="flex justify-between">
          <Button type="button" variant="outline" onClick={() => navigate("/")}>
            Back
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Running Analysis..." : "Run Analysis"}
          </Button>
        </div>
      </Card>
    </form>
  );
}
