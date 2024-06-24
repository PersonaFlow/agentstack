"use client";
import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { AssistentBuilder } from "./assistant-builder";

export default function BuildPanel() {
  const [isOpen, setIsOpen] = useState(false);

  const drawerStyles = {
    open: "p-4 border-solid border-2 h-full flex flex-col gap-4 overflow-x-hidden sm:min-w-[520px]",
    closed: "hidden",
  };

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
        <AssistentBuilder />
      </div>
    </div>
  );
}