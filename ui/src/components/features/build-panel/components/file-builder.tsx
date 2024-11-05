import { useFileStream } from "@/hooks/useFileStream";
import FilesDialog from "./files-dialog";
import SelectFiles from "./select-files";

export default function FileBuilder() {
    const { startProgressStream } = useFileStream();
    return (
      <div className="flex flex-col">
        <FilesDialog
          classNames="mb-4"
          startProgressStream={startProgressStream}
        />
        <SelectFiles />
      </div>
    );
}