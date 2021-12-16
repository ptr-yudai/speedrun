import "./App.css";
import 'react-toastify/dist/ReactToastify.css';
import Index from "./view/Index";
import Login from "./view/Login";
import Task from "./view/Task";
import AdminTasks from "./view/AdminTasks";
import { HashRouter, Routes, Route, Link } from "react-router-dom";
import { useLogin, useTasks, Tasks } from "./lib/api";
import { z } from "zod";
import { ToastContainer } from 'react-toastify';
import axios from "axios";
import logoURL from "./assets/image.png";

function App() {
  const { data: login, mutate: mutateLogin } = useLogin();
  const { data: tasks } = useTasks();

  const tasksByCategories = (tasks: z.infer<typeof Tasks>) => {
    let categories: string[] = [];
    tasks.forEach((t) => {
      if (categories.indexOf(t.category) === -1) {
        categories.push(t.category);
      }
    });
    categories.sort();

    return categories.map((c) => {
      const ts = tasks.filter((t) => t.category === c);
      ts.sort((a, b) => {
        if (a.id < b.id) {
          return -1;
        } else if (a.id > b.id) {
          return -1;
        } else {
          return 0;
        }
      });
      return {
        category: c,
        tasks: ts,
      };
    });
  };

  const logout = async () => {
    await axios.post("/logout")
    mutateLogin();
  };

  return (
    <HashRouter>
      <main>
        <nav>
          <div className="nav-item">
            <Link to="/">
              <img src={logoURL} className="nav-item-logo" />
            </Link>
          </div>
          {login ? (
            <>
              <div className="nav-item">{login.username}</div>
              <div className="nav-item">
                <a href="#" onClick={() => logout()}>ログアウト</a>
              </div>
            </>
          ) : (
            <div className="nav-item">
              <Link to="/login">ログイン</Link>
            </div>
          )}

          {(login && login.is_admin) && (
            <>
              <div className="nav-item"><Link to="/admin/tasks">問題管理</Link></div>
              <div className="nav-item"><Link to="/admin/users">プレイヤー管理</Link></div>
            </>
          )}

          {tasks &&
            tasksByCategories(tasks).map((xs) => (
              <div key={xs.category}>
                <div className="nav-item category">{xs.category}</div>
                {xs.tasks.map((t) => (
                  <div className="nav-item task" key={t.id}>
                    <Link to={`/task/${t.id}`}>{t.name}</Link>
                  </div>
                ))}
              </div>
            ))}
        </nav>

        <div className="view">
          <div className="wrapper">
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/task/:id" element={<Task />} />

              <Route path="/admin/tasks" element={<AdminTasks />} />
            </Routes>
          </div>
        </div>
      </main>
      <ToastContainer />
    </HashRouter>
  );
}

export default App;
