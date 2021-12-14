import{ useParams } from "react-router-dom";
import { useTask, useLogin, Login, Task as TaskSchema } from "../lib/api";
import { z } from "zod";
import { useInterval } from "usehooks-ts";
import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from 'react-toastify';

type LoginType = NonNullable<z.infer<typeof Login>>;

const solveSchema = TaskSchema.shape.solves.element;
type SolveType = z.infer<typeof solveSchema>;

const getAttempt = (task_id: string, login: LoginType) => {
  for (const attempt of login.attempts) {
    if (attempt.task_id === task_id) {
      return attempt;
    }
  }
  return undefined;
}

interface TaskImplProps {
  id: string;
}

interface SubmitResult {
  solved: boolean;
}

const TaskImpl = ({ id }: TaskImplProps) => {
  const { data: task, error, mutate: updateTask } = useTask(id);
  const { data: login, mutate: updateLogin } = useLogin();
  const attempt = login ? getAttempt(id, login) : undefined;
  const [ currentTime, setCurrentTime ] = useState("");
  const [ flag, setFlag ] = useState("");

  useEffect(() => {
    setFlag("");
  }, [ id ]);

  const canSubmit = (task && (
    (task.is_freezed === true) || attempt !== undefined
  ))
  const submit = async () => {
    const res = await axios.post<SubmitResult>(`/task/${id}/submit`, {
      flag: flag,
    })
    if (res.data.solved) {
      toast.success("Correct!");
      updateTask();
      updateLogin();
    } else {
      toast.error("Wrong...");
    }
  }

  const startAttempt = async () => {
    await axios.post(`/task/${id}/start`)
    toast.info("You started to attempt!");
    updateTask();
    updateLogin();
  }

  const orderByTime = (xs: SolveType[]) => {
    let ys = Array.from([...xs]);
    ys.sort((a, b) => {
      const x = a.finish_at - a.start_at;
      const y = b.finish_at - b.start_at;
      return x - y;
    })
    return ys;
  }

  useInterval(() => {
    setCurrentTime(() => {
      if (attempt) {
        const t = (Date.now().valueOf() - attempt.start_at*1000) / 1000;
        return t.toFixed(2);
      } else {
        return "";
      }
    })
  }, 10)

  if (error) {
    return <>...</>;
  }
  if (!task) {
    return <>Not Found</>;
  }

  return (
    <div className="wrapper">
      <h2>{task.name}</h2>
      <div>{task.category}</div>

      {task.description && (
        <>
          <div dangerouslySetInnerHTML={{__html: task.description}}></div>
          {task.has_attachment && (
            <p><a href={`/task/${task.id}/attachment.tar.gz`} download>DOWNLOAD ATTACHMENT</a></p>
          )}
        </>
      )}
      <div>author: {task.author}</div>

      {attempt ? (
        <>
          {attempt.finish_at ? (
            <>Your time is: {(attempt.finish_at - attempt.start_at).toFixed(2)} seconds</>
          ) : (
            <>Your time is {currentTime} seconds</>
          )}
        </>
      ) : (
        <>
          {(login && !task.is_freezed) && (
            <button onClick={() => startAttempt()}>Start</button>
          )}
        </>
      )}

      {canSubmit && (
        <form onSubmit={() => submit()}>
          <input type="text" value={flag} onChange={(e) => setFlag(e.target.value)} placeholder="RTACON{...}" />
          <button>Submit</button>
        </form>
      )}


      <div>
        <h3>Speedrun Ranking</h3>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>User</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {orderByTime(task.solves).map((solve, idx) => (
              <tr key={solve.user_id}>
                <td>{idx + 1}</td>
                <td>{solve.username}</td>
                <td>{(solve.finish_at - solve.start_at).toFixed(2)} sec</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

const Task = () => {
  const { id } = useParams();

  if (!id) {
    return <>Not Found</>
  }
  return <TaskImpl id={id} />
}
export default Task;
