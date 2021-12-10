<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import Router, {link} from 'svelte-spa-router'
  import { routes } from './routes.ts'
  import { messages, loginuser } from './lib/stores.ts';
</script>

<header>
  <h1>RTACON 2021</h1>
  <nav>
    <div>RTACON</div>
    <div>問題</div>
    <div>順位表</div>
    {#if !$loginuser}
      <div><a href="/login" use:link>ログイン</a></div>
    {:else}
      <div>{$loginuser.username}</div>
    {/if}
  </nav>
</header>

<main>
  <Router {routes}/>
</main>

<div class="messages">
  {#each $messages as message (message.id)}
    <div class={"message " + message.type} in:fade out:fade>{message.message}</div>
  {/each}
</div>

<style>
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
