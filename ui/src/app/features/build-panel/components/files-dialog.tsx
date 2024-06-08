import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FileIcon } from "@radix-ui/react-icons";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { UseFormReturn } from "react-hook-form";
import { SquarePlus } from "lucide-react";
import SelectFiles from "./select-files";
import MultiSelect from "@/components/ui/multiselect";
import {
  useDeleteAssistantFile,
  useDeleteFile,
  useFiles,
  useUploadFile,
} from "@/data-provider/query-service";
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
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <MultiSelect
                        values={values}
                        placecholder="Select a file..."
                        defaultValues={formattedAssistantFiles}
                        onValueChange={(selections) => {
                          const fileIds = getFileIds(selections);
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
                  <Label htmlFor="file" className="text-sm font-medium">
                    File
                  </Label>
                  <Input
                    id="file"
                    type="file"
                    placeholder="File"
                    accept="pdf/*"
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button size="lg">Upload</Button>
              </CardFooter>
            </Card>
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
