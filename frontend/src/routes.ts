import Counter from './view/Counter.svelte';
import Index from './view/Index.svelte';
import Login from './view/Login.svelte';
import Task from './view/Task.svelte';


export const routes = {
  '/': Index,
  '/counter': Counter,
  '/login': Login,
  '/task/:taskid': Task,
}
