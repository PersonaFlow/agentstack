import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FileIcon } from "@radix-ui/react-icons";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { UseFormReturn } from "react-hook-form";
import { SquarePlus } from "lucide-react";
import MultiSelect from "@/components/ui/multiselect";
import { useFiles, useUploadFile } from "@/data-provider/query-service";
import Spinner from "@/components/ui/spinner";
import { useEffect, useState } from "react";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";

type TFilesDialog = {
  form: UseFormReturn<any>;
};

type TOption = {
  label: string;
  value: string;
};

export default function FilesDialog({ form }: TFilesDialog) {
  const [fileUpload, setFileUpload] = useState<File>();
  const [values, setValues] = useState<TOption[]>([]);
  const { data: files, isLoading } = useFiles("1234");

  const uploadFile = useUploadFile();

  const { file_ids } = form.getValues();

  const formattedAssistantFiles = files?.reduce((files, file) => {
    if (file_ids.includes(file.id)) {
      files.push({ label: file.filename, value: file.id });
    }
    return files;
  }, [] as TOption[]);

  useEffect(() => {
    if (files) {
      const formattedFileData = files.map((file) => ({
        label: file.filename,
        value: file.id,
      }));

      setValues(formattedFileData);
    }
  }, [files]);

  const getFileIds = (selections: TOption[]) =>
    selections.map((selection) => selection.value);

  const handleUpload = () => {
    if (fileUpload) {
      const formData = new FormData();
      formData.append("file", fileUpload);
      formData.append("purpose", "assistants");
      formData.append("user_id", "1234");
      formData.append("filename", "fileName");
      uploadFile.mutate(formData, {
        onSuccess: () => console.log("success!"),
      });
    }
  };

  if (isLoading) return <Spinner />;

  return (
    <Dialog>
      <DialogTrigger className="flex gap-2 border-2 rounded-md p-2 border-black">
        <SquarePlus />
        Add Files
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="mb-3">Add Files</DialogTitle>
          <DialogDescription>
            <FormField
              control={form.control}
              name="file_ids"
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-col">
                    <FormLabel>Add assistant files</FormLabel>
                    <FormControl>
                      <MultiSelect
                        values={values}
                        placecholder="Select a file..."
                        defaultValues={formattedAssistantFiles}
                        onValueChange={(selections) => {
                          const fileIds = getFileIds(selections);
                          console.log(fileIds);
                          field.onChange(fileIds);
                        }}
                      />
                    </FormControl>
                  </FormItem>
                );
              }}
            />
            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="border-2 border-dashed border-gray-200 rounded-lg flex flex-col gap-1 p-6 items-center">
                  <FileIcon className="w-12 h-12" />
                  <span className="text-sm font-medium text-gray-500">
                    Drag and drop a file or click to browse
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <Label>File upload</Label>
                  <Input
                    placeholder="Picture"
                    type="file"
                    accept="image/*, application/pdf"
                    onChange={(event) => {
                      if (event.target.files) {
                        setFileUpload(event.target.files[0]);
                      }
                    }}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  disabled={!fileUpload}
                  size="lg"
                  type="button"
                  onClick={handleUpload}
                >
                  Upload file
                </Button>
              </CardFooter>
            </Card>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button size="lg" type="button">
              Close
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
