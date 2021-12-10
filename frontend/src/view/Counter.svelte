<script lang="ts">
import { count } from '../lib/stores.ts';

const countUp = () => {
  count.update(n => n + 1);
}

</script>

<div>
  <button on:click={countUp}>{$count}</button>
</div>
