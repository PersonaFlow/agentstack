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
  const [fileOptions, setFileOptions] = useState<TOption[]>([]);
  const { data: files, isLoading } = useFiles("1234");

  const uploadFile = useUploadFile();
  // const deleteFile = useDeleteFile();
  const deleteAssistantFile = useDeleteAssistantFile();

  useEffect(() => {
    if (files) {
      const multiSelectData = files.map((file) => ({
        label: file.filename,
        value: file.id,
      }));

      setFileOptions(multiSelectData);
    }
  }, [files]);

  // const {} = form.getValues().config.configurable;

  const handleChange = (selection: TOption) => {
    const fileId = selection.value;
    // const _selections = new Set(selections);
    // const _fileOptions = new Set(fileOptions);

    // const newSelections = [..._selections].filter(
    //   (element) => !_fileOptions.has(element),
    // );

    // const deletedSelections = [..._fileOptions].filter(
    //   (element) => !_selections.has(element),
    // );

    // if (newSelections.length > 0) {
    //   uploadFile();
    // }

    const deletedSelection = fileOptions.includes(selection);
    const newSelection = !deletedSelection;

    console.log("newSelections");
    console.log(newSelection);
    console.log("deletedSelections");
    console.log(deletedSelection);

    console.log(deletedSelection);
    deletedSelection ? deleteAssistantFile.mutate(fileId) : uploadFile(fileId);
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
                  <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                    <FormControl>
                      <div>
                        <MultiSelect
                          options={fileOptions}
                          placecholder="Select a file..."
                          defaultOptions={fileOptions}
                          onValueChange={(selections) =>
                            handleChange(selections)
                          }
                        />
                      </div>
                    </FormControl>
                    <FormLabel className="text-sm font-normal">
                      {file.filename}
                    </FormLabel>
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
