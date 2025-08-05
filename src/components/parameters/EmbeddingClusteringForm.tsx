
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface EmbeddingClusteringFormProps {
  embeddingType: string;
  clusteringMethod: string;
  onNext: () => void;
  onChange: (name: string, value: string) => void;
}

const EmbeddingClusteringForm = ({ embeddingType, clusteringMethod, onNext, onChange }: EmbeddingClusteringFormProps) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium">Embedding and Clustering Settings</h2>
        <p className="mt-2 text-sm text-gray-500">
          {/* Space for future description */}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="embeddingType">Embedding Type</Label>
          <Select 
            value={embeddingType}
            onValueChange={(value) => onChange("embeddingType", value)}
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
          <Label htmlFor="clusteringMethod">Clustering Method</Label>
          <Select
            value={clusteringMethod}
            onValueChange={(value) => onChange("clusteringMethod", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select clustering method" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="kmeans">K-Means</SelectItem>
              <SelectItem value="hac">HAC</SelectItem>
              <SelectItem value="gmm">GMM</SelectItem>
              <SelectItem value="birch">BIRCH</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <Button onClick={onNext} className="w-full mt-6">
        Next
      </Button>
    </div>
  );
};

export default EmbeddingClusteringForm;
