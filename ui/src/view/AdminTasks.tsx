import { useAdminTasks, useTasks } from "../lib/api";
import axios from "axios";

const AdminTasks = () => {
  const { data, mutate } = useAdminTasks();
  const { mutate: taskMutate } = useTasks();

  const toggleOpen = async (id: string) => {
    if (!data) {
      return;
    }
    for (const task of data) {
      if (task.id === id) {
        if (task.is_open) {
          await axios.post(`/admin/close/${id}`);
          mutate();
          taskMutate();
        } else {
          await axios.post(`/admin/open/${id}`);
          mutate();
          taskMutate();
        }
        break;
      }
    }
  }

  const toggleFreeze = async (id: string) => {
    if (!data) {
      return;
    }
    for (const task of data) {
      if (task.id === id) {
        if (task.is_freezed) {
          await axios.post(`/admin/unfreeze/${id}`);
          mutate();
          taskMutate();
        } else {
          await axios.post(`/admin/freeze/${id}`);
          mutate();
        }
        break;
      }
    }
  }

  if (!data) {
    return <>...</>;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>CATEGORY</th>
          <th>NAME</th>
          <th>ATTACHMENT</th>
          <th>OPENED</th>
          <th>TRYABLE</th>
        </tr>
      </thead>
      <tbody>
        {data.map((task) => (
          <tr key={task.id}>
            <td>
              <strong>{task.category}</strong>
            </td>

            <td>
              <strong>{task.name}</strong>
            </td>

            <td>
              {task.has_attachment && (
                <a href={`/task/${task.id}/attachment.tar.gz`} download>DOWNLOAD</a>
              )}
            </td>

            <td>
              {task.is_open ? "OPENED" : "CLOSED"}
              <input type="checkbox" checked={task.is_open} onChange={() => toggleOpen(task.id)} />
            </td>

            <td>
              {task.is_freezed ? "FREEZED" : "TRYABLE"}
              <input type="checkbox" checked={!task.is_freezed} onChange={() => toggleFreeze(task.id)} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AdminTasks;
