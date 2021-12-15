import { useLogin } from "../lib/api";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import axios from "axios";

const Login = () => {
  const { mutate } = useLogin();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const doLogin = async () => {
    try {
      await axios.post("/login", {
        username,
        password,
      });
      toast.success("logged in");
      navigate("/");
      mutate();
    } catch {}
  };

  const doRegister = async () => {
    try {
      await axios.post("/register", {
        username,
        password,
      });
      toast.success("registered and logged in");
      navigate("/");
      mutate();
    } catch {}
  };

  return (
    <form>
      <div className="form-item">
        <label>ユーザ名</label>
        <input
          type="text"
          placeholder="kurenaif"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>

      <div className="form-item">
        <label>パスワード</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <div>
        <button onClick={() => doLogin()}>ログイン</button>
        <button style={{marginLeft: '1em', display: 'inline-block'}} onClick={() => doRegister()}>登録</button>
      </div>
    </form>
  );
};
export default Login;
