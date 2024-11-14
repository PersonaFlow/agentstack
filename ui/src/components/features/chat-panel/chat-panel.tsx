"use client";

import { useGenerateTitle } from "@/data-provider/query-service";
import { MessageType, TMessage } from "@/data-provider/types";
import {
  useIsStreamDone,
  useIsStreaming,
  useStartStream,
  useStopStream,
  useStream as useStreamState,
} from "@/hooks/stream";
import { useSlugRoutes } from "@/hooks/useSlugParams";
// import { useStream } from "@/hooks/useStream";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Composer } from "./components/composer";
import MessagesContainer from "./components/messages-container";

export default function ChatPanel() {
  const [userMessage, setUserMessage] = useState("");
  const [isNewThread, setIsNewThread] = useState(false);
  const isStreaming = useIsStreaming();
  const isStreamDone = useIsStreamDone();
  // const { stream, startStream, stopStream: handleStop } = useStream();
  const startStream = useStartStream();
  const stopStream = useStopStream();
  const stream = useStreamState();
  const generateTitle = useGenerateTitle();
  const { assistantId, threadId } = useSlugRoutes();
  const router = useRouter();
  // const messages = useAtomValue(mergedMessagesAtom);

  useEffect(() => {
    if (isNewThread && isStreamDone && stream) {
      // console.log("chat panel", { messages, streamMessages: stream?.messages });
      generateTitle.mutate({
        thread_id: stream?.thread_id as string,
        history: (stream.messages as TMessage[]) || [],
      });

      router.push(`/a/${assistantId}/c/${stream?.thread_id}`);
    }
  }, [isStreamDone, isNewThread, assistantId, stream]);

  const handleStop = stopStream;
  const handleSend = async () => {
    const input = [
      {
        content: userMessage,
        type: MessageType.HUMAN,
        example: false,
      },
    ];

    setUserMessage("");

    if (!threadId) setIsNewThread(true);

    await startStream({
      input,
      thread_id: threadId as string,
      assistant_id: assistantId as string,
    });
  };

  return (
    <div className="h-full w-full gap-4 flex flex-col" data-testid="chat-panel">
      <div className="h-full flex flex-col rounded">
        {!assistantId ? (
          <div className="self-center h-full items-center flex">
            <h1 className="bg-sky-100 border border-blue-400 text-blue-700 px-4 py-3 rounded relative">
              {"Select an assistant to begin a conversation"}
            </h1>
          </div>
        ) : (
          <>
            {threadId || isNewThread ? (
              <MessagesContainer
                threadId={threadId}
                startStream={startStream}
              />
            ) : (
              <div className="self-center h-full items-center flex">
                <h1 className="bg-sky-100 border border-blue-400 text-blue-700 px-4 py-3 rounded relative">
                  {"Message the assisstant"}
                </h1>
              </div>
            )}
          </>
        )}

        <Composer
          onChange={(e) => setUserMessage(e.target.value)}
          value={userMessage}
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={!assistantId}
        />
      </div>
    </div>
  );
}

[
  {
    content: "hey",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "23e5eb4d-fae4-4fa3-a4b5-8fd6bb28e274",
    example: false,
  },
  {
    content: "Hello! How can I assist you today?",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-3247e609-4318-4259-ae93-0d5c66ae1c1d",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
  {
    content: "how to check break fluid",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "76ab8e50-9bb1-4ebb-87e8-7e6b11869f78",
    example: false,
  },
  {
    content:
      "To check the brake fluid level in your vehicle, you can follow these steps:\n\n1. Park your car on a level surface and turn off the engine.\n2. Open the hood of your car and locate the brake fluid reservoir. It is usually located near the back of the engine compartment on the driver's side.\n3. The reservoir is typically a translucent plastic container with minimum and maximum level markings on the side.\n4. Wipe the top of the reservoir clean with a cloth to ensure no dirt or debris falls into the brake fluid when you open it.\n5. Check the brake fluid level against the minimum and maximum markings on the side of the reservoir. If the level is below the minimum mark, you may need to add more brake fluid.\n6. If you need to add brake fluid, unscrew the cap on the reservoir and carefully pour in the appropriate type of brake fluid until it reaches the maximum level mark.\n7. Close the reservoir cap securely and make sure there are no leaks.\n\nIt's important to use the correct type of brake fluid recommended by your vehicle's manufacturer. If you are unsure or uncomfortable checking the brake fluid level yourself, it's best to have a professional mechanic inspect it for you.",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-f0929aeb-c1b1-482c-8b8a-939de1ac87c7",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
  {
    content: "how to check bushings",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "a8e8cb7a-2c28-44c4-888c-24ebe3d91a08",
    example: false,
  },
  {
    content:
      "To check the bushings in your vehicle, you can follow these steps:\n\n1. Park your car on a level surface and engage the parking brake.\n2. Get underneath the vehicle or use a flashlight to inspect the bushings. Bushings are rubber or polyurethane components that provide cushioning and reduce vibration between moving parts.\n3. Look for signs of wear, cracking, or deterioration on the bushings. They may appear cracked, torn, or distorted if they are worn out.\n4. Check for any excessive movement or play in the suspension components where the bushings are located. You can do this by gently pushing or pulling on the affected parts to see if there is any noticeable movement.\n5. Inspect the bushings for any signs of leakage, which could indicate that they are damaged and need to be replaced.\n6. If you notice any issues with the bushings, such as wear, damage, or excessive movement, it is recommended to have them inspected and replaced by a qualified mechanic.\n\nRegularly checking and maintaining the bushings in your vehicle can help ensure a smooth and comfortable ride, as well as prevent potential suspension issues.",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-2c851d3b-f648-4541-9441-bbae7ecf1b41",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
  {
    content: "hi",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "4ba205d9-5dca-4377-a67f-edab6ab3edbd",
    example: false,
  },
  {
    content: "Hello! How can I assist you today?",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-15edd9e7-04b4-41c8-8698-50a85668c214",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
  {
    content: "hi",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "9f0e54b9-b940-4f20-94be-50e05164c0c2",
    example: false,
  },
  {
    content: "Hello! How can I help you today?",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-7bd615e1-1d03-4c17-b7f6-4b4eacd9ff67",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
  {
    content: "tell me how to check ball joints",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "1d399c46-1046-4ef4-9036-4471f541041f",
    example: false,
  },
  {
    content:
      "To check the ball joints in your vehicle, you can follow these steps:\n\n1. Park your car on a level surface and engage the parking brake.\n2. Jack up the front of the vehicle and support it securely with jack stands.\n3. Locate the ball joints on the front suspension. Ball joints are spherical bearings that connect the control arms to the steering knuckles.\n4. Inspect the ball joints visually for any signs of wear, damage, or looseness. Look for excessive play or movement in the ball joints.\n5. You can also perform a physical check by using a pry bar or a large screwdriver to apply pressure to the ball joint while someone else observes for any movement or play.\n6. Check for any unusual noises such as clunking or squeaking when turning the steering wheel or going over bumps, as these could indicate worn ball joints.\n7. If you notice any signs of wear, damage, or excessive play in the ball joints, it is recommended to have them inspected and replaced by a qualified mechanic.\n\nRegularly checking and maintaining the ball joints in your vehicle is important for safe and reliable operation of the suspension system. If you are unsure about checking the ball joints yourself, it's best to have a professional mechanic inspect them for you.",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-8f6084f5-e05c-44e4-854f-bc7f872c74ee",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
  {
    content: "how to check what is leaking in the engine bay",
    additional_kwargs: { example: false },
    response_metadata: {},
    type: "human",
    name: null,
    id: "34e1de13-bc18-4068-b5f4-af49991eef12",
    example: false,
  },
  {
    content:
      "To determine what is leaking in the engine bay of your vehicle, you can follow these steps:\n\n1. Park your car on a level surface and allow the engine to cool down before inspecting for leaks.\n2. Open the hood of your car and visually inspect the engine bay for any signs of fluid leaks. Common fluids that may leak from a vehicle include engine oil, coolant, power steering fluid, brake fluid, and transmission fluid.\n3. Look for puddles or drips of fluid on the ground underneath the engine bay, as this can help you identify the source of the leak.\n4. Check the engine components, hoses, and connections for any visible signs of leaks. Look for wet spots, stains, or drips on the engine block, hoses, radiator, power steering pump, brake master cylinder, or transmission.\n5. If you are unable to identify the source of the leak visually, you can use a clean rag or paper towel to wipe down the suspected areas and check for fresh leaks after running the engine for a short period of time.\n6. Pay attention to any unusual smells or smoke coming from the engine bay, as this can also help you identify the type of fluid leaking.\n7. If you are still unable to determine the source of the leak, it is recommended to have a professional mechanic inspect your vehicle to diagnose and repair the issue.\n\nIdentifying and addressing fluid leaks in the engine bay promptly can help prevent further damage to your vehicle and ensure safe operation on the road.",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-84ae9ffb-2d0d-4ed5-94c2-5c5e1e9c7ce5",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
];

[
  {
    content:
      "To determine what is leaking in the engine bay of your vehicle, you can follow these steps:\n\n1. Park your car on a level surface and allow the engine to cool down before inspecting for leaks.\n2. Open the hood of your car and visually inspect the engine bay for any signs of fluid leaks. Common fluids that may leak from a vehicle include engine oil, coolant, power steering fluid, brake fluid, and transmission fluid.\n3. Look for puddles or drips of fluid on the ground underneath the engine bay, as this can help you identify the source of the leak.\n4. Check the engine components, hoses, and connections for any visible signs of leaks. Look for wet spots, stains, or drips on the engine block, hoses, radiator, power steering pump, brake master cylinder, or transmission.\n5. If you are unable to identify the source of the leak visually, you can use a clean rag or paper towel to wipe down the suspected areas and check for fresh leaks after running the engine for a short period of time.\n6. Pay attention to any unusual smells or smoke coming from the engine bay, as this can also help you identify the type of fluid leaking.\n7. If you are still unable to determine the source of the leak, it is recommended to have a professional mechanic inspect your vehicle to diagnose and repair the issue.\n\nIdentifying and addressing fluid leaks in the engine bay promptly can help prevent further damage to your vehicle and ensure safe operation on the road.",
    additional_kwargs: {},
    response_metadata: { finish_reason: "stop" },
    type: "ai",
    name: null,
    id: "run-84ae9ffb-2d0d-4ed5-94c2-5c5e1e9c7ce5",
    example: false,
    tool_calls: [],
    invalid_tool_calls: [],
  },
];
