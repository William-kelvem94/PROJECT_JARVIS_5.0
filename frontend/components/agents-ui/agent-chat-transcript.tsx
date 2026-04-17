'use client';

import { AnimatePresence } from 'motion/react';
import { AgentChatIndicator } from '@/components/agents-ui/agent-chat-indicator';
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation';
import { Message, MessageContent, MessageResponse } from '@/components/ai-elements/message';
import { type Message as JarvisMessage } from '@/context/JarvisContext';
import { type AgentState } from '@/types/agent';

/**
 * Props for the AgentChatTranscript component.
 */
export interface AgentChatTranscriptProps {
  /**
   * The current state of the agent. When 'thinking', displays a loading indicator.
   */
  agentState?: AgentState;
  /**
   * Array of messages to display in the transcript.
   * @defaultValue []
   */
  messages?: JarvisMessage[];
  /**
   * Additional CSS class names to apply to the conversation container.
   */
  className?: string;
}

/**
 * A chat transcript component that displays a conversation between the user and agent.
 */
export function AgentChatTranscript({
  agentState,
  messages = [],
  className,
  ...props
}: AgentChatTranscriptProps) {
  return (
    <Conversation className={className} {...props}>
      <ConversationContent tabIndex={undefined}>
        {messages.map((msg, idx) => {
          const { role, content, timestamp } = msg;

          return (
            <Message key={idx} title={timestamp} from={role}>
              <MessageContent tabIndex={undefined}>
                <MessageResponse>{content}</MessageResponse>
              </MessageContent>
            </Message>
          );
        })}
        <AnimatePresence mode="popLayout">
          {agentState === 'thinking' && <AgentChatIndicator size="sm" />}
        </AnimatePresence>
      </ConversationContent>
      <ConversationScrollButton />
    </Conversation>
  );
}
