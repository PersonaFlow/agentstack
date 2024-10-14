import FilesDialog from "./files-dialog";
import SelectFiles from "./select-files";

export default function FileBuilder() {
    return (
      <div className="flex flex-col">
        <FilesDialog classNames="mb-4" />
        {/* <SelectFiles form={form} /> */}
      </div>
    );
}