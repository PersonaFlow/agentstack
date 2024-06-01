"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { useAssistants } from "@/data-provider/query-service";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { ChevronLeft, ChevronRight } from "lucide-react";

const mockFiles = [
  {
    filename: "a.pdf",
    id: "1",
  },
  {
    filename: "b.pdf",
    id: "2",
  },
  {
    filename: "c.pdf",
    id: "3",
  },
  {
    filename: "d.pdf",
    id: "4",
  },
  {
    filename: "e.pdf",
    id: "5",
  },
  {
    filename: "f.pdf",
    id: "6",
  },
  {
    filename: "g.pdf",
    id: "7",
  },
  {
    filename: "h.pdf",
    id: "8",
  },
  {
    filename: "i.pdf",
    id: "9",
  },
  {
    filename: "j.pdf",
    id: "10",
  },
];

const formSchema = z.object({
  public: z.boolean(),
  name: z.string(),
  config: z.object({
    configurable: z.object({
      interrupt_before_action: z.boolean(),
      type: z.string(),
      agent_type: z.string().optional(),
      llm_type: z.string(),
      retrieval_description: z.string(),
      system_message: z.string(),
      tools: z.array(z.string()),
    }),
  }),
  file_ids: z.array(z.string()),
});

const defaultValues = {
  public: false,
  name: undefined,
  config: {
    configurable: {
      interrupt_before_action: false,
      type: "agent",
      agent_type: "GPT 3.5 Turbo",
      llm_type: "GPT 3.5 Turbo",
      retrieval_description:
        "Can be used to look up information that was uploaded for this assistant.",
      system_message: "You are a helpful assistant.",
      tools: [],
    },
  },
  file_ids: [],
};

const tools = [
  "DDG Search",
  "Search (Tavily)",
  "Search (short answer, Tavily)",
  "Retrieval",
  "Arxiv",
  "PubMed",
  "Wikipedia",
];

export default function Builder() {
  // Note: we prob want to retrieve assistants by userId
  const { data: assistantsData, isLoading } = useAssistants();
  const [selectedAssistant, setSelectedAssistant] = useState("");
  const [isOpen, setIsOpen] = useState(true);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: defaultValues,
  });

  const botType = form.watch("config.configurable.type");

  const drawerStyles = {
    open: "p-4 border-solid border-2 h-full flex flex-col gap-4 overflow-x-hidden min-w-[340px] sm:min-w-[352px]",
    closed:
      "p-4 border-solid border-2 h-full flex flex-col gap-4 overflow-x-hidden min-w-[50px]",
  };

  useEffect(() => {
    if (botType !== "agent") {
      // Set undefined agent_type if bot is not an agent
      form.setValue("config.configurable.agent_type", undefined);
    }
  }, [botType]);

  // Seems to be rendering a million times, but why...
  // console.log("render");

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
    // createAssistant.mutate(values);
  }

  if (isLoading || !assistantsData) return <div></div>;

  return (
    <div className="flex items-center">
      {isOpen ? (
        <ChevronRight
          className="cursor-pointer"
          onClick={() => setIsOpen((prev) => !prev)}
        />
      ) : (
        <ChevronLeft
          className="cursor-pointer"
          onClick={() => setIsOpen((prev) => !prev)}
        />
      )}
      <div className={isOpen ? drawerStyles["open"] : drawerStyles["closed"]}>
        <Select
          onValueChange={(value) => setSelectedAssistant(value)}
          defaultValue={
            assistantsData.length > 0
              ? assistantsData[0].name
              : selectedAssistant
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {assistantsData.map((assistant) => (
              <SelectItem value={assistant.name}>{assistant.name}</SelectItem>
            ))}
            <SelectItem value="create-assistant">Create Assistant</SelectItem>
          </SelectContent>
        </Select>
        <SelectSeparator />

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <Accordion type="multiple">
              <AccordionItem value="Assistant Builder">
                <AccordionTrigger>Build Assistants</AccordionTrigger>
                <AccordionContent className="overflow-y-scroll h-[200px]">
                  <div className="flex gap-6">
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
                              onCheckedChange={(checked) =>
                                field.onChange(checked)
                              }
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
                          <FormLabel>Bot Type</FormLabel>
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
                    {form.getValues().config.configurable.type === "agent" && (
                      <FormField
                        control={form.control}
                        name="config.configurable.agent_type"
                        render={({ field }) => (
                          <FormItem className="flex flex-col">
                            <FormLabel>Agent Type</FormLabel>
                            <FormControl>
                              <Select
                                // value={form.getValues().config.configurable.type !== "agent" && undefined}
                                onValueChange={field.onChange}
                                defaultValue={field.value}
                              >
                                <SelectTrigger className="w-[180px]">
                                  <SelectValue placeholder="Select Agent Type" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="GPT 3.5 Turbo">
                                    GPT 3.5 Turbo
                                  </SelectItem>
                                  <SelectItem value="GPT 4 Turbo">
                                    GPT 4 Turbo
                                  </SelectItem>
                                  <SelectItem value="GPT 4 (Azure OpenAI)">
                                    GPT 4 (Azure OpenAI)
                                  </SelectItem>
                                  <SelectItem value="Claude 2">
                                    Claude 2
                                  </SelectItem>
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
                    )}
                  </div>
                  <FormField
                    control={form.control}
                    name="config.configurable.llm_type"
                    render={({ field }) => (
                      <FormItem className="flex flex-col">
                        <FormLabel>LLM Type</FormLabel>
                        <FormControl>
                          <Select
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                          >
                            <SelectTrigger className="w-[180px]">
                              <SelectValue placeholder="LLM Type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="GPT 3.5 Turbo">
                                GPT 3.5 Turbo
                              </SelectItem>
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
                  <div>
                    {tools.map((tool) => (
                      <FormField
                        key={tool}
                        control={form.control}
                        name="config.configurable.tools"
                        render={({ field }) => {
                          return (
                            <FormItem
                              key={tool}
                              className="flex flex-row items-start space-x-3 space-y-0"
                            >
                              <FormControl>
                                <Checkbox
                                  checked={field.value?.includes(tool)}
                                  onCheckedChange={(checked) => {
                                    return checked
                                      ? field.onChange([...field.value, tool])
                                      : field.onChange(
                                          field.value?.filter(
                                            (value) => value !== tool,
                                          ),
                                        );
                                  }}
                                />
                              </FormControl>
                              <FormLabel className="text-sm font-normal">
                                {tool}
                              </FormLabel>
                            </FormItem>
                          );
                        }}
                      />
                    ))}
                  </div>
                  <FormField
                    control={form.control}
                    name="config.configurable.interrupt_before_action"
                    render={({ field }) => {
                      return (
                        <FormItem className="flex flex-col gap-2">
                          <FormLabel>Interrupt before action?</FormLabel>
                          <Switch
                            onCheckedChange={(checked) =>
                              field.onChange(checked)
                            }
                          />
                        </FormItem>
                      );
                    }}
                  />
                  <FormField
                    control={form.control}
                    name="config.configurable.retrieval_description"
                    render={({ field }) => {
                      return (
                        <FormItem className="flex flex-col gap-2">
                          <FormLabel>Retrieval Description</FormLabel>
                          <Textarea {...field} />
                        </FormItem>
                      );
                    }}
                  />
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="files">
                <AccordionTrigger>Upload Files</AccordionTrigger>
                <AccordionContent className="overflow-y-scroll h-[200px]">
                  {mockFiles.map((file) => (
                    <FormField
                      key={file.id}
                      control={form.control}
                      name="file_ids"
                      render={({ field }) => {
                        return (
                          <FormItem
                            key={file.id}
                            className="flex flex-row items-start space-x-3 space-y-0"
                          >
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(file.id)}
                                onCheckedChange={(checked) => {
                                  return checked
                                    ? field.onChange([...field.value, file.id])
                                    : field.onChange(
                                        field.value?.filter(
                                          (value) => value !== file.id,
                                        ),
                                      );
                                }}
                              />
                            </FormControl>
                            <FormLabel className="text-sm font-normal">
                              {file.filename}
                            </FormLabel>
                          </FormItem>
                        );
                      }}
                    />
                  ))}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </form>
        </Form>
      </div>
    </div>
  );
}
