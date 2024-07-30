import { render, screen } from "@testing-library/react";
import { CreateAssistant } from "../create-assistant";
import {
  useRunnableConfigSchema,
  useFiles,
} from "@/data-provider/query-service";
import mockConfigSchema from "./config-schema.data.json";
import userEvent from "@testing-library/user-event";

jest.mock("@/data-provider/query-service");

async function selectOption({
  selectName,
  optionName,
}: {
  selectName: string | RegExp;
  optionName: string | RegExp;
}) {
  await userEvent.click(screen.getByRole("combobox", { name: selectName }));
  await userEvent.click(
    await screen.findByRole("option", { name: optionName }),
  );
}

test("renders chatbot assistant create form", async () => {
  (useRunnableConfigSchema as jest.Mock).mockReturnValue({
    data: mockConfigSchema,
    isLoading: false,
    isError: false,
  });

  render(<CreateAssistant onAssistantCreated={jest.fn()} />);

  expect(screen.getByRole("textbox", { name: /assistant name/i })).toHaveValue(
    "",
  );
  expect(screen.getByRole("switch", { name: /public/i })).not.toBeChecked();

  await selectOption({
    selectName: /architecture/i,
    optionName: /chatbot/i,
  });

  await screen.findByRole("combobox", { name: /llm type/i });
  screen.getByRole("textbox", { name: /system prompt/i });

  screen.getByRole("button", { name: /save/i });
});

test("renders chat retrieval assistant create form", async () => {
  (useRunnableConfigSchema as jest.Mock).mockReturnValue({
    data: mockConfigSchema,
    isLoading: false,
    isError: false,
  });
  (useFiles as jest.Mock).mockReturnValue({
    data: [],
    isLoading: false,
    isError: false,
  });

  render(<CreateAssistant onAssistantCreated={jest.fn()} />);

  screen.getByRole("textbox", { name: /assistant name/i });
  expect(screen.getByRole("switch", { name: /public/i })).not.toBeChecked();

  await selectOption({
    selectName: /architecture/i,
    optionName: /chat_retrieval/i,
  });

  screen.getByRole("combobox", { name: /llm type/i });
  screen.getByRole("textbox", { name: /system prompt/i });

  await userEvent.click(screen.getByRole("button", { name: /capabilities/i }));
  await screen.findByRole("checkbox", { name: /retrieval/i, checked: true });

  screen.getByText(/Retrieval Instructions/i);
  screen.getByRole("button", { name: /add files/i });
  await userEvent.click(screen.getByText(/options/i));
  await screen.findByRole("checkbox", { name: /Interrupt before action/i });

  screen.getByRole("button", { name: /save/i });
});

test("renders agent assistant create form", async () => {
  (useRunnableConfigSchema as jest.Mock).mockReturnValue({
    data: mockConfigSchema,
    isLoading: false,
    isError: false,
  });
  (useFiles as jest.Mock).mockReturnValue({
    data: [],
    isLoading: false,
    isError: false,
  });

  render(<CreateAssistant onAssistantCreated={jest.fn()} />);

  expect(screen.getByRole("textbox", { name: /assistant name/i })).toHaveValue(
    "",
  );
  expect(screen.getByRole("switch", { name: /public/i })).not.toBeChecked();

  await selectOption({
    selectName: /architecture/i,
    optionName: /agent/i,
  });

  screen.getByRole("combobox", { name: /model/i });
  screen.getByRole("textbox", { name: /system prompt/i });

  await userEvent.click(screen.getByRole("button", { name: /capabilities/i }));
  await screen.findByRole("checkbox", { name: /retrieval/i, checked: false });
  screen.getByText(/Retrieval Instructions/i);
  screen.getByRole("button", { name: /add files/i });
  screen.getByRole("button", { name: /Tools/i });
  await userEvent.click(screen.getByText(/options/i));
  await screen.findByRole("checkbox", { name: /Interrupt before action/i });

  screen.getByRole("button", { name: /save/i });
});
