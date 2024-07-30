import { render, screen } from "@testing-library/react";
import { EditAssistant } from "../edit-assistant";
import {
  useRunnableConfigSchema,
  useFiles,
} from "@/data-provider/query-service";
import mockConfigSchema from "./config-schema.data.json";
import userEvent from "@testing-library/user-event";

jest.mock("@/data-provider/query-service");

test("renders chatbot assistant edit form", async () => {
  (useRunnableConfigSchema as jest.Mock).mockReturnValue({
    data: mockConfigSchema,
    isLoading: false,
    isError: false,
  });

  const assistant = {
    id: "123",
    user_id: "default",
    name: "First Assisstant",
    config: {
      configurable: {
        type: "chatbot",
        agent_type: "GPT 3.5 Turbo",
        interrupt_before_action: false,
        retrieval_description:
          "Can be used to look up information that was uploaded to this assistant.\nIf the user is referencing particular files, that is often a good hint that information may be here.\nIf the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!",
        system_message: "You are a helpful assistant.",
        tools: [],
        llm_type: "GPT 3.5 Turbo",
      },
    },
    kwargs: null,
    file_ids: [],
    public: true,
    created_at: "2024-07-08T00:26:05+00:00",
    updated_at: "2024-07-08T00:26:05+00:00",
  };
  render(<EditAssistant assistant={assistant} />);

  expect(screen.getByRole("textbox", { name: /assistant name/i })).toHaveValue(
    assistant.name,
  );
  expect(screen.getByRole("switch", { name: /public/i })).toBeChecked();

  screen.getByRole("combobox", { name: /architecture/i });
  screen.getByRole("combobox", { name: /llm type/i });
  screen.getByRole("textbox", { name: /system prompt/i });

  screen.getByRole("button", { name: /save/i });
});

test("renders chat retrieval assistant edit form", async () => {
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

  const assistant = {
    id: "123",
    user_id: "default",
    name: "chat retrieval",
    config: {
      configurable: {
        type: "chat_retrieval",
        agent_type: "GPT 3.5 Turbo",
        interrupt_before_action: false,
        retrieval_description:
          "Can be used to look up information that was uploaded to this assistant.\nIf the user is referencing particular files, that is often a good hint that information may be here.\nIf the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!",
        system_message: "You are a helpful assistant.",
        tools: [
          {
            type: "retrieval",
            description: "Look up information in uploaded files.",
            name: "Retrieval",
            config: {},
            multi_use: false,
          },
        ],
        llm_type: "GPT 3.5 Turbo",
      },
    },
    kwargs: null,
    file_ids: [],
    public: false,
    created_at: "2024-07-20T21:01:18+00:00",
    updated_at: "2024-07-20T21:01:18+00:00",
  };

  render(<EditAssistant assistant={assistant} />);

  expect(screen.getByRole("textbox", { name: /assistant name/i })).toHaveValue(
    assistant.name,
  );
  expect(screen.getByRole("switch", { name: /public/i })).not.toBeChecked();

  screen.getByRole("combobox", { name: /architecture/i });
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

test("renders agent assistant edit form", async () => {
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

  const assistant = {
    id: "565",
    user_id: "default",
    name: "agent arch",
    config: {
      configurable: {
        type: "agent",
        agent_type: "GPT 3.5 Turbo",
        interrupt_before_action: true,
        retrieval_description:
          "Can be used to look up information that was uploaded to this assistant.\nIf the user is referencing particular files, that is often a good hint that information may be here.\nIf the user asks a vague question, they are likely meaning to look up info from this retriever, and you should call it!",
        system_message: "You are a helpful assistant.",
        tools: [
          {
            type: "action_server_by_robocorp",
            description:
              "Run AI actions with [Sema4.ai Action Server](https://github.com/Sema4AI/actions).",
            name: "Action Server by Sem4.ai",
            config: {},
            multi_use: true,
          },
        ],
        llm_type: "GPT 3.5 Turbo",
      },
    },
    kwargs: null,
    file_ids: [],
    public: true,
    created_at: "2024-07-25T05:56:09+00:00",
    updated_at: "2024-07-25T05:57:54+00:00",
  };

  render(<EditAssistant assistant={assistant} />);

  expect(screen.getByRole("textbox", { name: /assistant name/i })).toHaveValue(
    assistant.name,
  );
  expect(screen.getByRole("switch", { name: /public/i })).toBeChecked();

  screen.getByRole("combobox", { name: /architecture/i });
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
