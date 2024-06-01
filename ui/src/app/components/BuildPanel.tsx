"use client";
import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { OpenedPanel } from "./OpenedPanel";
import { ClosedPanel } from "./ClosedPanel";

export default function BuildPanel() {
  const [isOpen, setIsOpen] = useState(true);

  const drawerStyles = {
    open: "p-4 border-solid border-2 h-full flex flex-col gap-4 overflow-x-hidden sm:min-w-[520px]",
    closed:
      // "p-4 border-solid border-2 h-full flex flex-col gap-4 overflow-x-hidden min-w-[50px]",
      "hidden",
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
        {/* {isOpen ? <OpenedPanel /> : <ClosedPanel />} */}
        <OpenedPanel />
      </div>
    </div>
  );
}
