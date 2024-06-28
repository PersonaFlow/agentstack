import { useStreamChat } from "@/data-provider/query-service";
import { MessageType, TMessage } from "@/data-provider/types";
import { assistantAtom, conversationAtom } from "@/store";
import { useAtom } from "jotai";
import { useCallback, useState } from "react";

export const useChat = (threadId: string) => {
  const [userMessage, setUserMessage] = useState("");
  const [conversation, setConversation] = useAtom(conversationAtom);
  const [assistant, setAssistant] = useAtom(assistantAtom);
  const stream = useStreamChat();

  const [current, setCurrent] = useState<StreamState | null>(null);
  const [controller, setController] = useState<AbortController | null>(null);

  const startStream = useCallback(
    async (
      input: TMessage[] | Record<string, any> | null,
      thread_id: string,
      config?: Record<string, unknown>,
    ) => {
      const controller = new AbortController();
      setController(controller);
      setCurrent({ status: "inflight", messages: input || [] });

      console.log(input);

      await fetchEventSource("/runs/stream", {
        signal: controller.signal,
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input, thread_id, config }),
        openWhenHidden: true,
        onmessage(msg) {
          if (msg.event === "data") {
            const messages = JSON.parse(msg.data);
            setCurrent((current) => ({
              status: "inflight" as StreamState["status"],
              messages: mergeMessagesById(current?.messages, messages),
              run_id: current?.run_id,
            }));
          } else if (msg.event === "metadata") {
            const { run_id } = JSON.parse(msg.data);
            setCurrent((current) => ({
              status: "inflight",
              messages: current?.messages,
              run_id: run_id,
            }));
          } else if (msg.event === "error") {
            setCurrent((current) => ({
              status: "error",
              messages: current?.messages,
              run_id: current?.run_id,
            }));
          }
        },
        onclose() {
          setCurrent((current) => ({
            status: current?.status === "error" ? current.status : "done",
            messages: current?.messages,
            run_id: current?.run_id,
          }));
          setController(null);
        },
        onerror(error) {
          setCurrent((current) => ({
            status: "error",
            messages: current?.messages,
            run_id: current?.run_id,
          }));
          setController(null);
          throw error;
        },
      });
    },
    [],
  );

  const handleSend = () => {
    if (!conversation) return null;

    setConversation((prevConversation) => [...prevConversation, userMessage]);
    console.log(assistant?.id);
    const payload = {
      user_id: "1234",
      thread_id: threadId,
      assistant_id: assistant.id,
      input: [
        {
          content: userMessage,
          role: MessageType.HUMAN,
          example: false,
        },
      ],
    };

    stream.mutate(payload, {
      onSuccess: (res) => console.log(res),
    });
  };

  return {
    handleSend,
    userMessage,
    setUserMessage,
  };
};
