import { z } from "zod";
import useSWR from "swr";
import axios from "axios";


export const Login = z.object({
  id: z.string(),
  username: z.string(),
  is_admin: z.boolean(),
  is_runner: z.boolean(),
  attempts: z.array(z.object({
    user_id: z.string(),
    task_id: z.string(),
    start_at: z.number(),
    finish_at: z.number().nullable(),
  })),
}).nullable()

export const useLogin = () => {
  return useSWR('/info', async () => {
    const res = await axios.get("/info")
    return Login.parse(res.data);
  })
}

export const Tasks = z.array(z.object({
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

export const useTasks = () => {
  return useSWR('/tasks', async () => {
    const res = await axios.get("/tasks")
    return Tasks.parse(res.data);
  })
}

export const Task = z.object({
  id: z.string(),
  name: z.string(),
  category: z.string(),
  description: z.string().nullable(),
  is_freezed: z.boolean(),
  has_attachment: z.boolean(),
  author: z.string(),
  solves: z.array(z.object({
    user_id: z.string(),
    username: z.string(),
    is_runner: z.boolean(),
    start_at: z.number(),
    finish_at: z.number(),
  })),
})

export const useTask = (id: string) => {
  return useSWR(id, async () => {
    const res = await axios.get(`/task/${id}`)
    return Task.parse(res.data);
  })
}

export const AdminTasks = z.array(z.object({
  id: z.string(),
  name: z.string(),
  category: z.string(),
  description: z.string(),
  has_attachment: z.boolean(),
  is_freezed: z.boolean(),
  is_open: z.boolean(),
  author: z.string(),
}))

export const useAdminTasks = () => {
  return useSWR('/admin/tasks', async () => {
    const res = await axios.get('/admin/tasks')
    return AdminTasks.parse(res.data);
  })
}

export const Users = z.array(z.object({
  id: z.string(),
  username: z.string(),
  is_runner: z.boolean(),
  is_admin: z.boolean(),
}))

export const useUsers = () => {
  return useSWR('/admin/users', async () => {
    const res = await axios.get('/admin/users')
    return Users.parse(res.data);
  })
}

