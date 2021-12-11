<script lang="ts">
  import { fade }  from 'svelte/transition';
  import Router, {link} from 'svelte-spa-router'
  import { routes } from './routes'
  import { messages, loginuser, tasks } from './lib/stores';
  import { Login } from './lib/schema';
  import type { z } from "zod";
  import { TaskList } from "./lib/schema"
  import axios from "axios";

  const checkLogin = async () => {
    const res = await axios.get("/info");
    const info = Login.parse(res.data);
    loginuser.update(() => info);
  }
  const loadTasks = async () => {
    const res = await axios.get("/tasks")
    tasks.update(() => TaskList.parse(res.data));
  }

  const tasksByCategories = (tasks: z.infer<typeof TaskList>) => {
    let categories: string[] = [];
    tasks.forEach(t => {
      if (categories.indexOf(t.category) === -1) {
        categories.push(t.category);
      }
    })
    categories.sort();

    return categories.map(c => {
      const ts = tasks.filter(t => t.category === c);
      ts.sort((a, b) => { 
        if (a.id < b.id) { return -1; }
        else if (a.id > b.id) { return -1; }
        else { return 0; }
      })
      return {
        category: c,
        tasks: ts,
      };
    })
  }

  checkLogin()
  loadTasks()
  
</script>

<main>
  <nav>
    <div class="nav-item"><a href="/" use:link>RTACON</a></div>
    <div class="nav-item"><a href="/ranking" use:link>順位表</a></div>
    {#if !$loginuser}
      <div class="nav-item"><a href="/login" use:link>ログイン</a></div>
    {:else}
      <div class="nav-item">{$loginuser.username}</div>
    {/if}
    <div class="divider"></div>
    {#each tasksByCategories($tasks) as taskByCat}
        <div class="nav-item category">{taskByCat.category}</div>
          {#each taskByCat.tasks as t}
            <div class="nav-item task">
              <a href={`/task/${t.id}`} use:link>{t.name}</a>
            </div>
          {/each}
    {/each}
  </nav>
  <div class="pageview">
    <Router {routes}/>
  </div>
</main>

<div class="messages">
  {#each $messages as message (message.id)}
    <div class={"message " + message.type} in:fade out:fade>{message.message}</div>
  {/each}
</div>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300&display=swap');
* {
  font-family: 'Noto Sans JP', sans-serif;
}
:root {
  font-size: 24px;
}


main {
  display: flex;
}

nav {
  min-width: max-content;
  min-height: 100vh;
  border-right: 1px solid #0070F333;
  overflow: hidden;
}

.pageview {
  flex: 1;
}

.nav-item {
  width: 100%;
  padding-top: 0.25em;
  padding-bottom: 0.25em;
  padding-right: 2em;
  padding-left: 1em;

  position: relative;
  overflow: hidden;
}
.nav-item a {
  display: block;
  width: 100%;
  height: 100%;
  text-decoration: none;
  color: inherit;
}
.nav-item a:after {
  content: '';
  display: block;
  position: absolute;
  top: -200%;
  left: -25%;
  width: 100%;
  height: 500%;
  background: #00000033;
  border-radius: 100%;
  opacity: 0;
}
@keyframes navhover {
  0% {
    transform: scale(0);
    opacity: 0.4;
  }
  50% {
    transform: scale(1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 0.1;
  }
}
.nav-item a:hover:after {
  animation: navhover 1s ease-out;
}

.nav-item.category {
  font-weight: bold;
}
.nav-item.task {
  padding-top: 0.1em;
  padding-bottom: 0.1em;
  padding-left: 2em;
}

.messages {
  position: fixed;
  top: 0;
  right: 0;
}
.messages .message {
  min-width: 200px;
  padding:  0.5em 1em;
  margin: 1em;
}

.message.info {
  border: #0070F3 solid 1px;
  background-color: #0070F333;
}

.message.error {
  border: #f30053 solid 1px;
  background-color: #f3005333;
}
</style>
