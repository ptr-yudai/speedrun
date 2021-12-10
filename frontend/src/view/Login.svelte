<script lang="ts">
  import axios from "axios";
  import { loginuser } from "../lib/stores.ts";
  import { Login } from "../lib/schema.ts";

  let username = '';
  let password = '';

  const login = async () => {
    const res = await axios.post("/login", {
      username: username,
      password: password,
    }, {
      withCredentials: true,
    })
    const data = await Login.parse(res.data)
    loginuser.update(() => data);
  }

  const register = () => {
    axios.post("/register", {
      username: username,
      password: password,
    }, {
      withCredentials: true,
    })
  }
</script>

<div>
  <form>
    <div>
      <label>ユーザ名</label>
      <input type="text" placeholder="kurenaif" bind:value={username} required>
    </div>

    <div>
      <label>パスワード</label>
      <input type="password" bind:value={password} required>
    </div>

    <div>
      <input type="button" value="ログイン" on:click={login} />
      <input type="button" value="登録" on:click={register} />
    </div>
  </form>
</div>

<style>
label {
  display: block;
  font-size: 75%;
  font-weight: bold;
}
</style>
