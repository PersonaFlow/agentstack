"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { useCreateAssistant, useFiles } from "@/data-provider/query-service";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";

const formSchema = z.object({
  public: z.boolean(),
  name: z.string(),
  config: z.object({
    configurable: z.object({
      interrupt_before_action: z.boolean(),
      type: z.string(),
      agent_type: z.string(),
      llm_type: z.string(),
      retrieval_description: z.string(),
      system_message: z.string(),
    }),
  }),
  file_ids: z.array(z.string()),
});

export default function Page() {
  const { data: userFiles } = useFiles("1234");
  const createAssistant = useCreateAssistant();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      public: false,
      name: "",
      config: {
        configurable: {
          interrupt_before_action: false,
          type: "agent",
          agent_type: "GPT 3.5 Turbo",
          llm_type: "GPT 3.5 Turbo",
          retrieval_description:
            "Can be used to look up information that was uploaded for this assistant.",
          system_message: "You are a helpful assistant.",
        },
      },
      file_ids: [],
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    createAssistant.mutate(values);
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="p-6 border-solid border-2 w-full gap-4 flex flex-col"
      >
        <h1>Create Assistant</h1>
        <div className="flex gap-12 items-center">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <Input
                    placeholder="Assistant Name"
                    type="text"
                    {...field}
                    className="w-[400px]"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="public"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormLabel>Public</FormLabel>
                <FormControl>
                  <Switch
                    onCheckedChange={(checked) => field.onChange(checked)}
                  />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <div className="flex gap-6">
          <FormField
            control={form.control}
            name="config.configurable.type"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormControl>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Bot Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="chatbot">Chatbot</SelectItem>
                      <SelectItem value="chat_retrieval">
                        Chat Retrieval
                      </SelectItem>
                      <SelectItem value="agent">Agent</SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="config.configurable.agent_type"
            render={({ field }) => (
              <FormItem className="flex flex-col">
                <FormControl>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Agent Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GPT 3.5 Turbo">
                        GPT 3.5 Turbo
                      </SelectItem>
                      <SelectItem value="GPT 4 Turbo">GPT 4 Turbo</SelectItem>
                      <SelectItem value="GPT 4 (Azure OpenAI)">
                        GPT 4 (Azure OpenAI)
                      </SelectItem>
                      <SelectItem value="Claude 2">Claude 2</SelectItem>
                      <SelectItem value="Claude 2 (Amazon Bedrock)">
                        Claude 2 (Amazon Bedrock)
                      </SelectItem>
                      <SelectItem value="GEMINI">GEMINI</SelectItem>
                      <SelectItem value="Ollama">Ollama</SelectItem>
                    </SelectContent>
                  </Select>
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="config.configurable.llm_type"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormControl>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="LLM Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="GPT 3.5 Turbo">GPT 3.5 Turbo</SelectItem>
                    <SelectItem value="GPT 4">GPT 4</SelectItem>
                    <SelectItem value="GPT 4 (Azure OpenAI)">
                      GPT 4 (Azure OpenAI)
                    </SelectItem>
                    <SelectItem value="Claude 2">Claude 2</SelectItem>
                    <SelectItem value="Claude 2 (Amazon Bedrock)">
                      Claude 2 (Amazon Bedrock)
                    </SelectItem>
                    <SelectItem value="GEMINI">GEMINI</SelectItem>
                    <SelectItem value="Ollama">Ollama</SelectItem>
                    <SelectItem value="Mixtral">Mixtral</SelectItem>
                  </SelectContent>
                </Select>
              </FormControl>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="config.configurable.system_message"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>System Message</FormLabel>
              <FormControl>
                <Textarea
                  {...field}
                  className="w-[400px]"
                  placeholder="Instructions for the assistant. ex: 'You are a helpful assistant'"
                />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="flex gap-4">
          {userFiles?.length > 0 && (
            <FormField
              control={form.control}
              name="file_ids"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Retrieval descriptio</FormLabel>
                  <FormControl>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Files" />
                      </SelectTrigger>
                      <SelectContent>
                        {userFiles?.map((file) => (
                          <SelectItem value={file.id}>
                            {file.filename}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </FormControl>
                </FormItem>
              )}
            />
          )}
          {/* <Button className="w-40"> */}
          {/* Add new file */}
          {/* <Input type="file" /> */}
          {/* </Button> */}
        </div>

        {/* <FormField
          control={form.control}
          name="retrieval_description"
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Retrieval description</FormLabel>
              <FormControl>
                <Textarea
                  className="w-[400px]"
                  placeholder="Used to look up information that was uploaded for this assistant."
                />
              </FormControl>
            </FormItem>
          )}
        />
        <div className="flex items-center gap-2">
          <Label htmlFor="interrupt_before_action">
            Interrupt before action?
          </Label>
          <Switch id="interrupt_before_action" />
        </div> */}
        <Button type="submit" className="w-40">
          Submit
        </Button>
      </form>
    </Form>
  );
}
