<script lang="ts">
  import { toast } from "../lib/stores/toast.svelte";
</script>

<div class="toasts">
  {#each toast.items as t (t.id)}
    <button class="toast {t.type}" onclick={() => toast.dismiss(t.id)}>
      {t.message}
    </button>
  {/each}
</div>

<style>
  .toasts {
    position: fixed;
    bottom: 20px;
    right: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    z-index: 200;
    max-width: 380px;
  }
  .toast {
    text-align: left;
    padding: 12px 16px;
    border-radius: 10px;
    border: none;
    color: #fff;
    font-weight: 500;
    box-shadow: 0 6px 20px rgb(15 23 42 / 0.25);
    cursor: pointer;
  }
  .toast.success { background: var(--success); }
  .toast.error { background: var(--danger); }
  .toast.info { background: var(--primary); }
  .toast:hover { filter: brightness(1.08); background: inherit; }
  .toast.success:hover { background: var(--success); }
  .toast.error:hover { background: var(--danger); }
  .toast.info:hover { background: var(--primary); }
</style>
