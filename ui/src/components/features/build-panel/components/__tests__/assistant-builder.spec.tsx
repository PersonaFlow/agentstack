import { render, screen } from "@testing-library/react";
import { AssistentBuilder } from "../assistant-builder";
import { useParams } from "next/navigation";
import {
  useAssistant,
  useThread,
  useAssistants,
} from "@/data-provider/query-service";

jest.mock("../edit-assistant", () => {
  return {
    EditAssistant: jest.fn(() => <div>EditAssistant</div>),
  };
});
jest.mock("../create-assistant", () => {
  return {
    CreateAssistant: jest.fn(() => <div>CreateAssistant</div>),
  };
});

jest.mock("next/navigation", () => {
  return {
    useParams: jest.fn(),
  };
});
jest.mock("@/data-provider/query-service", () => {
  return {
    useAssistant: jest.fn(),
    useThread: jest.fn(),
    useAssistants: jest.fn(),
  };
});

test("should render", () => {
  (useParams as jest.Mock).mockReturnValue({ id: "1" });
  (useThread as jest.Mock).mockReturnValue({ data: { assistant_id: "1" } });
  (useAssistant as jest.Mock).mockReturnValue({ data: { id: "1" } });
  (useAssistants as jest.Mock).mockReturnValue({ data: [{ id: "1" }] });

  render(<AssistentBuilder />);

  screen.getByRole("button", { name: "Create Assistant" });
  expect(screen.getByText("EditAssistant")).toBeInTheDocument();
  expect(screen.queryByText("CreateAssistant")).toBeNull();
});
