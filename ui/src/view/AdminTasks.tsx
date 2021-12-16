import { z } from "zod";
import { AdminTasks as AdminTasksSchema } from "../lib/api";
import { useAdminTasks, useTasks } from "../lib/api";
import axios from "axios";

type Task = typeof AdminTasksSchema.element;
type TaskType = z.infer<Task>;

const AdminTasks = () => {
  const { data, mutate } = useAdminTasks();
  const { mutate: taskMutate } = useTasks();

  const toggleOpen = async (task: TaskType) => {
    if (task.is_open) {
      await axios.post(`/admin/close/${task.id}`);
      mutate();
      taskMutate();
    } else {
      await axios.post(`/admin/open/${task.id}`);
      mutate();
      taskMutate();
    }
  }

  const toggleFreeze = async (task: TaskType) => {
    if (!data) {
      return;
    }
    if (task.is_freezed) {
      await axios.post(`/admin/unfreeze/${task.id}`);
      mutate();
      taskMutate();
    } else {
      await axios.post(`/admin/freeze/${task.id}`);
      mutate();
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
              OPENED
              <input type="checkbox" checked={task.is_open} onChange={() => toggleOpen(task)} />
            </td>

            <td>
              TRYABLE
              <input type="checkbox" checked={!task.is_freezed} onChange={() => toggleFreeze(task)} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AdminTasks;
