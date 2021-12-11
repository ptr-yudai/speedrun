import { z } from "zod";

export const Login = z.object({
  id: z.string(),
  username: z.string(),
  is_admin: z.boolean(),
  is_runner: z.boolean(),
  attempts: z.array(z.object({
    user_id: z.string(),
    task_id: z.string(),
    start_at: z.number(),
    finish_at: z.number().optional(),
  })),
})

export const TaskList = z.array(z.object({
  id: z.string(),
  name: z.string(),
  category: z.string(),
  author: z.string(),
  solves: z.array(z.object({
    user_id: z.string(),
    username: z.string(),
    is_runner: z.boolean(),
    start_at: z.number(),
    finish_at: z.number(),
  })),
}))

export const Task = z.object({
  id: z.string(),
  name: z.string(),
  category: z.string(),
  description: z.string().optional(),
  author: z.string(),
  solves: z.array(z.object({
    user_id: z.string(),
    username: z.string(),
    is_runner: z.boolean(),
    start_at: z.number(),
    finish_at: z.number(),
  })),
})
