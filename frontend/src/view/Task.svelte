<script lang="ts">
  import axios from "axios";
  import { z } from "zod";
  import type { TaskList, Login } from "../lib/schema";
  import { Task } from "../lib/schema";
  import { tasks, loginuser } from "../lib/stores";

  type ParamType = {
    taskid?: string;
  }
  export let params: ParamType = {};

  type Attempt = {
    start_at: number;
    finish_at: number|undefined;
  }

  let login: z.infer<typeof Login>|null = null;
  let taskInfo: z.infer<typeof Task>|null = null;
  loginuser.subscribe(async u => {
    login = u;

    if (!u) {
      return;
    }
    for (const a of u.attempts) {
      if (a.task_id === params.taskid) {
        taskInfo = await getTask(a.task_id);
      }
    }
  })

  let task: z.infer<typeof TaskList.element>|null = null;
  // reactive
  $: tasks.subscribe(ts => {
    const t = ts.filter(t => t.id === params.taskid);
    if (t.length === 1) {
      task = t[0]
    }
  })

  const getTask = async (taskid: string) => {
    const res = await axios.get(`/task/${taskid}`)
    return Task.parse(res.data)
  }

</script>

<div class="wrapper">
  {#if task === null}
    <div>...</div>
  {:else}
    <div>
      <h2>{task.name}</h2>
      <div>{task.category}</div>
      {#if taskInfo}
        <div>{@html taskInfo.description}</div>
        <div style="text-align: right;">author: {task.author}</div>
        <div>
          <input type="text" placeholder={'RTACON{.+}'}>
        </div>
      {:else}
        <div style="text-align: right;">author: {task.author}</div>
        <div class="start"><button>START</button></div>
      {/if}
    </div>
  {/if}
</div>

<style>
.wrapper {
  width: 768px;
  margin: 20px auto;
}

.start {
  text-align: center;
}
.start button {
  background: transparent;
  border: 2px solid #000000;
  border-radius: 2px;
  padding: 0.5em 1em;
}
.start button:hover {
  cursor: pointer;
}
.start button:active {
  position: relative;
  top: 2px;
}
</style>

