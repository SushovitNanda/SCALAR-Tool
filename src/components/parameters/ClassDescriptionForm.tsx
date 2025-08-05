
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";

interface ClassDescriptionFormProps {
  numClasses: number;
  classDescriptions: { [key: string]: string };
  onBack: () => void;
  onSubmit: () => void;
  onClassDescriptionChange: (classNum: number, type: 'name' | 'description', value: string) => void;
}

const ClassDescriptionForm = ({ 
  numClasses, 
  classDescriptions, 
  onBack, 
  onSubmit,
  onClassDescriptionChange 
}: ClassDescriptionFormProps) => {
  const classArray = Array.from({ length: numClasses }, (_, i) => i);

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-medium mb-4">Class Descriptions</h2>
      <div className="space-y-4">
        {classArray.map((_, i) => (
          <Card key={i} className="p-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor={`class${i+1}_name`}>Class {i+1} Domain Name</Label>
                <Input
                  id={`class${i+1}_name`}
                  value={classDescriptions[`class${i+1}_name`] || ''}
                  onChange={(e) => onClassDescriptionChange(i+1, 'name', e.target.value)}
                  placeholder={`Enter class ${i+1} domain name`}
                />
              </div>
              <div>
                <Label htmlFor={`class${i+1}_desc`}>Class {i+1} Description</Label>
                <Input
                  id={`class${i+1}_desc`}
                  value={classDescriptions[`class${i+1}_desc`] || ''}
                  onChange={(e) => onClassDescriptionChange(i+1, 'description', e.target.value)}
                  placeholder={`Enter class ${i+1} description`}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>
      
      <div className="flex gap-4 mt-6">
        <Button variant="outline" onClick={onBack} className="w-full">
          Back
        </Button>
        <Button onClick={onSubmit} className="w-full">
          Run Analysis
        </Button>
      </div>
    </div>
  );
};

export default ClassDescriptionForm;
