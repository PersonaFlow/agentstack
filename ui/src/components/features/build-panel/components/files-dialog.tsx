import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";
import { FileIcon } from "@radix-ui/react-icons";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Plus } from "lucide-react";
import MultiSelect from "@/components/ui/multiselect";
import { useAssistant, useAssistantFiles, useFiles, useIngestFileData, useUploadFile } from "@/data-provider/query-service";
import Spinner from "@/components/ui/spinner";
import { ChangeEvent, useEffect, useMemo, useState } from "react";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
} from "@/components/ui/form";
import { useToast } from "@/components/ui/use-toast";
import { cn } from "@/utils/utils";
import { useSlugRoutes } from "@/hooks/useSlugParams";
import { fileIngestSchema } from "@/data-provider/types";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// TODO
// - Get assistant form default getRandomValues 
// - Get file default values

type TFilesDialog = {
  classNames: string;
};

type TOption = {
  label: string;
  value: string;
};

const defaultFormValues: z.infer<typeof fileIngestSchema> = {
  files: [],
  purpose: "assistants",
  namespace: "",
  document_processor: {
    summarize: false,
    encoder: {
      provider: "openai",
      encoder_model: "text-embedding-3-small",
      dimensions: 1536,
      score_threshold: 0.75,
    },
    unstructured: {
      partition_strategy: "auto",
      hi_res_model_name: "detectron2_onnx",
      process_tables: false,
    },
    splitter: {
      name: "semantic",
      min_tokens: 30,
      max_tokens: 280,
      rolling_window_size: 1,
      prefix_titles: true,
      prefix_summary: false,
    },
  },
};

export default function FilesDialog({ classNames }: TFilesDialog) {

  const { data: fileOptions, isLoading } = useFiles();

  const uploadFile = useUploadFile();

  const { assistantId } = useSlugRoutes();

  const { data: assistantFiles } = useAssistantFiles(assistantId as string);

  const { toast } = useToast();

  const ingestFiles = useIngestFileData();

  const form = useForm<z.infer<typeof fileIngestSchema>>({
    resolver: zodResolver(fileIngestSchema),
    defaultValues: useMemo(() => {
      if (assistantFiles && assistantId) {
        defaultFormValues.namespace = assistantId;
        defaultFormValues.files = assistantFiles.map(file => file.id);
      }
      return defaultFormValues;
    },[assistantFiles])
  });

  const { formState: { isDirty } } = form;

  const [fileUpload, setFileUpload] = useState<File | null>();
  const [values, setValues] = useState<TOption[]>([]);
  const [open, setOpen] = useState(false);

  //Update form defaultValues
  useEffect(() => {
    if (assistantFiles && assistantId) {
      defaultFormValues.namespace = assistantId;
      defaultFormValues.files = assistantFiles.map(file => file.id);
      console.log(defaultFormValues)
      form.reset(defaultFormValues);
    }
  }, [assistantFiles, assistantId]);

  // Format files for MultiSelect
  useEffect(() => {
    if (fileOptions) {
      const formattedFileData = fileOptions.map((file) => ({
        label: file.filename,
        value: file.id,
      }));

      setValues(formattedFileData);
    }
  }, [fileOptions]);

  const onSubmit = (values: z.infer<typeof fileIngestSchema>) => {
    console.log("values", values);
    ingestFiles.mutate(values, {
      onSuccess: ({ task_id }) => {
        
        setOpen(false);
      }
    });
  };

  const formattedAssistantFiles = fileOptions?.reduce((files, file) => {
    if (
      assistantFiles?.some((assistantFile) => assistantFile.id === file.id)
    ) {
      files.push({ label: file.filename, value: file.id });
    }
    return files;
  }, [] as TOption[]);

  const getFilesFromSelections = (selections: TOption[]) =>
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
        fileOptions?.some(
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
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        className={cn(
          buttonVariants({ variant: "outline" }),
          "gap-2",
          classNames,
        )}
        type="button"
      >
        <Plus />
        Manage Files
      </DialogTrigger>
      <DialogContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit, (e) => {
              console.log(e);
              console.log(form.getValues())
            })}
          >
            <DialogHeader>
              <DialogTitle className="mb-3 text-slate-300">
                Manage Files
              </DialogTitle>
            </DialogHeader>
            <DialogDescription>
              <FormField
                control={form.control}
                name="files"
                render={({ field }) => {
                  return (
                    <FormItem className="flex flex-col">
                      <FormControl>
                        <MultiSelect
                          values={values}
                          placecholder="Select a file..."
                          defaultValues={formattedAssistantFiles}
                          onValueChange={(selections) => {
                            const files = getFilesFromSelections(selections);
                            console.log(files);
                            field.onChange(files);
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
            <Button
              size="lg"
              type="submit"
              className="mt-4 ml-auto"
              disabled={!isDirty}
            >
              Save Files to Assistant
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
