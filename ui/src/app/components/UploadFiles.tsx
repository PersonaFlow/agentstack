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
import { Form, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useUploadFile } from "@/data-provider/query-service";
import { SquarePlus } from "lucide-react";

const formSchema = z.object({});

const defaultValues = {};

export default function UploadFiles() {
  //   const uploadFile = useUploadFile({
  //     userId,
  //   });
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues,
  });

  const onSubmit = (values: formSchema) => {
    console.log(values);
  };

  return (
    <Dialog>
      <DialogTrigger>
        <Button className="flex gap-2">
          <SquarePlus />
          Upload New File
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="mb-3">File Upload</DialogTitle>
          <DialogDescription>
            <Card>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)}>
                  <CardContent className="p-6 space-y-4">
                    <div className="border-2 border-dashed border-gray-200 rounded-lg flex flex-col gap-1 p-6 items-center">
                      <FileIcon className="w-12 h-12" />
                      <span className="text-sm font-medium text-gray-500">
                        Drag and drop a file or click to browse
                      </span>
                      {/* <span className="text-xs text-gray-500">PDF</span> */}
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
                </form>
              </Form>
            </Card>
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
