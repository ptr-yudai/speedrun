import { z } from "zod";
import type { Users } from "../lib/api";
import { useUsers } from "../lib/api";
import axios from "axios";

type User = typeof Users.element;
type UserType = z.infer<User>;

const AdminUsers = () => {
  const { data, mutate } = useUsers();

  const toggleRunner = async (user: UserType) => {
    if (!data) {
      return;
    }
    if (user.is_runner) {
        await axios.post(`/admin/user/${user.id}/make_not_runner`);
        mutate();
    } else {
        await axios.post(`/admin/user/${user.id}/make_runner`);
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
          <th>USERNAME</th>
          <th>IS_ADMIN</th>
          <th>IS_RUNNER</th>
        </tr>
      </thead>
      <tbody>
        {data.map((user) => (
          <tr key={user.id}>
            <td>
              <strong>{user.username}</strong>
            </td>

            <td>
              {user.is_admin && '😤'}
            </td>

            <td>
              <input type="checkbox" onChange={() => toggleRunner(user)} checked={user.is_runner} />
              {user.is_runner && '🏃'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AdminUsers;
