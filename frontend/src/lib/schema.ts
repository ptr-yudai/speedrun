import { z } from "zod";

export const Login = z.object({
  id: z.string(),
  username: z.string(),
  is_admin: z.boolean(),
  is_runner: z.boolean(),
})
