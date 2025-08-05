
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ClassSettingsFormProps {
  numClusters: string;
  minWikiPages: string;
  onNext: () => void;
  onBack: () => void;
  onChange: (name: string, value: string) => void;
}

const ClassSettingsForm = ({ numClusters, minWikiPages, onNext, onBack, onChange }: ClassSettingsFormProps) => {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-medium mb-4">Class Settings</h2>
      <div className="grid gap-4">
        <div className="space-y-2">
          <Label htmlFor="numClusters">Number of Classes/Labels</Label>
          <Select
            value={numClusters}
            onValueChange={(value) => onChange("numClusters", value)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select number of classes" />
            </SelectTrigger>
            <SelectContent>
              {[2, 3, 4, 5].map((num) => (
                <SelectItem key={num} value={num.toString()}>
                  {num} Classes
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="minWikiPages">Minimum Wikipedia Pages</Label>
          <Select
            value={minWikiPages}
            onValueChange={(value) => onChange("minWikiPages", value)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select minimum pages" />
            </SelectTrigger>
            <SelectContent>
              {Array.from({ length: 24 }, (_, i) => i + 2).map((num) => (
                <SelectItem key={num} value={num.toString()}>
                  {num} Pages
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-gray-500">Recommended: 2-25 pages</p>
        </div>
      </div>
      
      <div className="flex gap-4 mt-6">
        <Button variant="outline" onClick={onBack} className="w-full">
          Back
        </Button>
        <Button onClick={onNext} className="w-full">
          Next
        </Button>
      </div>
    </div>
  );
};

export default ClassSettingsForm;
