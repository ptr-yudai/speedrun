<script lang="ts">
  import axios from "axios";
  import { loginuser, messages } from "../lib/stores";
  import { Login } from "../lib/schema";

  let username = '';
  let password = '';

  const login = async () => {
    await axios.post("/login", {
      username: username,
      password: password,
    }, {
      withCredentials: true,
    })

    const res = await axios.get("/info", {
      withCredentials: true,
    })
    const data = await Login.parse(res.data)
    loginuser.update(() => data);
    messages.push("Successfully logged in", "info");
  
  }

  const register = async () => {
    axios.post("/register", {
      username: username,
      password: password,
    }, {
      withCredentials: true,
    })
    const res = await axios.get("/info", {
      withCredentials: true,
    })
    const data = await Login.parse(res.data)
    loginuser.update(() => data);
    messages.push("Successfully registered", "info");
  }
</script>

<div class="wrapper">
  <form>
    <div class="form-item">
      <label>ユーザ名</label>
      <input type="text" placeholder="kurenaif" bind:value={username} required>
    </div>

    <div class="form-item">
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
.wrapper {
  margin-top: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.form-item {
  margin-bottom: 1em;
}

input {
  font-size: inherit; 
}
input[type=text],input[type=password] {
  text-align: center;
  border: 1px solid #000000;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

label {
  display: block;
  font-size: 75%;
  font-weight: bold;
}
</style>
