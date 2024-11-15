"use client";

import { useFileStream } from "@/hooks/useFileStream";
import FilesDialog from "./files-dialog";
import SelectFiles from "./select-files";
import Spinner from "@/components/ui/spinner";

export default function FileBuilder() {
  const { startProgressStream, progressStream } = useFileStream();
  return (
    <div className="flex flex-col">
      <FilesDialog
        classNames="mb-4"
        startProgressStream={startProgressStream}
      />
      <SelectFiles />
      <div>
        {progressStream?.status === "error" && (
          <p>Something went wrong when ingesting files.</p>
        )}
        {progressStream?.status === "inflight" && (
          <Spinner />
        )}
      </div>
    </div>
  );
}
