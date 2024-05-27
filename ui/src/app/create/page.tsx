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
import { useFiles } from "@/data-provider/query-service";

export default function Page() {
  const { data: userFiles } = useFiles("1234");

  return (
    <div className="p-6 border-solid border-2 w-full">
      <div className="flex gap-8 align-center">
        <h1>Create Assistant</h1>
        <div className="flex items-center gap-2">
          <Label htmlFor="public">Public</Label>
          <Switch id="public" />
        </div>
      </div>
      <div className="my-6 gap-6 flex flex-col">
        <div className="grid w-full max-w-sm items-center gap-1.5">
          <Input id="name" type="text" placeholder="Assistant Name" />
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="interrupt_before_action">
            Interrupt before action?
          </Label>
          <Switch id="interrupt_before_action" />
        </div>
        <div className="flex flex-col gap-2">
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Bot Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="chatbot">Chatbot</SelectItem>
              <SelectItem value="chat_retrieval">Chat Retrieval</SelectItem>
              <SelectItem value="agent">Agent</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col gap-2">
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Agent Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="GPT 3.5 Turbo">GPT 3.5 Turbo</SelectItem>
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
        </div>
        <div className="flex flex-col gap-2">
          <Select>
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
        </div>
        <div>
          <Label htmlFor="retrieval_description">Retrieval description</Label>
          <Textarea
            className="w-[400px]"
            placeholder="Tool description providing instructions to the LLM for its use"
            id="retrieval_description"
          />
        </div>
        <div>
          <Label htmlFor="system_message">System Message</Label>
          <Textarea
            className="w-[400px]"
            placeholder="Instructions for the assistant. ex: 'You are a helpful assistant'"
            id="system_message"
          />
        </div>
      </div>
      <div className="flex flex-col gap-2">
        {userFiles && (
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Files" />
            </SelectTrigger>
            <SelectContent>
              {userFiles?.map((file) => (
                <SelectItem value={file.id}>{file.filename}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>
      <div className="grid w-full max-w-sm items-center gap-1.5">
        <Label htmlFor="add-file">Add new file</Label>
        <Input id="picture" type="file" />
      </div>
    </div>
  );
}
