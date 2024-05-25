"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

export default function Page() {
  return (
    <div className="p-6 border-solid border-2 w-full">
      <h1>Create Assistant</h1>
      <div className="my-6 gap-6 flex flex-col">
        <div className="flex flex-col gap-2">
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Model" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="model-one">Model one</SelectItem>
              <SelectItem value="model-two">Model two</SelectItem>
              <SelectItem value="model-three">Model three</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="preamble">Preamble</Label>
          <Textarea
            className="w-[400px]"
            placeholder="A string to override the preamble."
            id="preamble"
          />
        </div>
      </div>
      <div>
        <Label htmlFor="preamble">Files</Label>
        <Textarea
          className="w-[400px]"
          placeholder="A string to override the preamble."
          id="preamble"
        />
      </div>
    </div>
  );
}
