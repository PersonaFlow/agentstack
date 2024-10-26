import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";
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
import { Plus, SquarePlus } from "lucide-react";
import MultiSelect from "@/components/ui/multiselect";
import { useFiles, useUploadFile } from "@/data-provider/query-service";
import Spinner from "@/components/ui/spinner";
import { ChangeEvent, useEffect, useState } from "react";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/utils/utils";

type TFilesDialog = {
  form: UseFormReturn<any>;
  classNames: string;
};

type TOption = {
  label: string;
  value: string;
};

export default function FilesDialog({ form, classNames }: TFilesDialog) {
  const [fileUpload, setFileUpload] = useState<File | null>();
  const [values, setValues] = useState<TOption[]>([]);
  const { data: files, isLoading } = useFiles("assistants");

  const uploadFile = useUploadFile();

  const { file_ids } = form.getValues();

  const {toast} = useToast();

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
      // Note: Filename should be optional! Remove once bug is fixed.
      formData.append("filename", fileUpload.name);
      uploadFile.mutate(formData, {
        onSuccess: () => {
          setFileUpload(null);
          toast({
            variant: "default",
            title: "New file saved.",
          });
        },
        onError: () => {
          toast({
            variant: "destructive",
            title: "Something went wrong while saving file.",
          });
        },
      });
    }
  };

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
      if (event.target.files) {
        const selectedFiles = Array.from(event.target.files);
        const duplicateFiles = selectedFiles.filter((file) =>
          files?.some(
            (uploadedFile) =>
              uploadedFile.filename === file.name &&
              uploadedFile.bytes === file.size,
          ),
        );
        if (duplicateFiles.length > 0) {
          return toast({
            variant: "destructive",
            title: "Cannot add duplicate files.",
          });
        }
        setFileUpload(event.target.files[0]);
      }
    };

  if (isLoading) return <Spinner />;

  return (
    <Dialog>
      <DialogTrigger
        className={cn(buttonVariants({ variant: "outline" }), "gap-2", classNames)}
        type="button"
      >
        <Plus />
        Manage Files
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="mb-3 text-slate-300">Add Files</DialogTitle>
          <hr className="border-slate-400 pb-2" />
          <DialogDescription>
            <FormField
              control={form.control}
              name="file_ids"
              render={({ field }) => {
                return (
                  <FormItem className="flex flex-col">
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
            <Card className="bg-slate-200">
              <CardContent className="p-6 space-y-4">
                <div className="border-2 border-dashed border-gray-700 rounded-lg flex flex-col gap-1 p-6 items-center">
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
                      handleFileChange(event);
                    }}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  variant="default"
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
``      </DialogContent>
    </Dialog>
  );
}
