
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { toast } from "sonner";
import { uploadFile } from "@/services/analysisService";
import { useNavigate } from "react-router-dom";

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile?.type !== "text/csv" && !uploadedFile?.name.endsWith(".csv")) {
      toast.error("Please upload a CSV file");
      return;
    }
    setFile(uploadedFile);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    setIsUploading(true);
    try {
      await uploadFile(file);
      toast.success("File uploaded successfully");
      navigate("/parameters");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card className="p-6 border-2 border-dashed" {...getRootProps()}>
        <input {...getInputProps()} />
        <div className="text-center space-y-2">
          <div className="text-4xl mb-4">📄</div>
          {isDragActive ? (
            <p>Drop the CSV file here</p>
          ) : (
            <>
              <p>Drag & drop your CSV file here</p>
              <p className="text-sm text-muted-foreground">or click to select file</p>
            </>
          )}
        </div>
      </Card>

      {file && (
        <div className="flex items-center justify-between p-2 bg-muted rounded">
          <span className="text-sm truncate">{file.name}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFile(null)}
          >
            Remove
          </Button>
        </div>
      )}

      <Button 
        className="w-full" 
        disabled={!file || isUploading}
        onClick={handleUpload}
      >
        {isUploading ? "Uploading..." : "Upload & Continue"}
      </Button>
    </div>
  );
}
