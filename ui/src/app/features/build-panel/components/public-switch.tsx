import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { Switch } from "@/components/ui/switch";
import { UseFormProps, UseFormReturn } from "react-hook-form";

type TPublicSwitchProps = {
  form: UseFormReturn<any>;
};

export default function PublicSwitch({ form }: TPublicSwitchProps) {
  return (
    <FormField
      control={form.control}
      name="public"
      render={({ field }) => {
        console.log(field.value);
        return (
          <FormItem className="flex flex-col">
            <FormLabel>Public</FormLabel>
            <FormControl>
              <Switch
                defaultChecked={field.value}
                onCheckedChange={(checked) => field.onChange(checked)}
              />
            </FormControl>
          </FormItem>
        );
      }}
    />
  );
}
