import { writable } from 'svelte/store';
import type { Login } from './schema';
import type { z } from "zod";

export const count = writable(0);
export const loginuser = writable<z.infer<typeof Login>|null>(null);

export type MessageType = 'info'|'error';

type Message = {
  id: number;
  message: string;
  type: MessageType
};

const messages_ = writable<Message[]>([]);
const newMessage = (message: string, type: MessageType) => {
  const id = Date.now().valueOf();
  messages_.update(messages => messages.concat([{
    id,
    message,
    type,
  }]));
  setTimeout(() => {
    messages_.update(messages => messages.filter(x => x.id !== id));
  }, 3000);
}

export const messages = {
  subscribe: messages_.subscribe,
  push: newMessage,
}
