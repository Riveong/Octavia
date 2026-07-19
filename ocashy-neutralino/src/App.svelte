<script lang="ts">
  import Kasir from "./pages/Kasir.svelte";
  import Produk from "./pages/Produk.svelte";
  import Riwayat from "./pages/Riwayat.svelte";
  import Pengaturan from "./pages/Pengaturan.svelte";
  import Toasts from "./components/Toasts.svelte";

  type Page = "kasir" | "produk" | "riwayat" | "pengaturan";

  let page = $state<Page>("kasir");

  const menu: { id: Page; icon: string; label: string }[] = [
    { id: "kasir", icon: "🧾", label: "Kasir" },
    { id: "produk", icon: "📦", label: "Produk" },
    { id: "riwayat", icon: "🗂️", label: "Riwayat Nota" },
    { id: "pengaturan", icon: "⚙️", label: "Pengaturan" },
  ];
</script>

<div class="shell">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">O</div>
      <div>
        <div class="brand-name">Ocashy</div>
        <div class="brand-sub">Istana Keramik</div>
      </div>
    </div>

    <nav>
      {#each menu as m (m.id)}
        <button class="nav-item" class:active={page === m.id} onclick={() => (page = m.id)}>
          <span class="nav-icon">{m.icon}</span>
          {m.label}
        </button>
      {/each}
    </nav>

    <div class="sidebar-foot">v2.0 · Desktop</div>
  </aside>

  <main class="content">
    {#if page === "kasir"}
      <Kasir />
    {:else if page === "produk"}
      <Produk />
    {:else if page === "riwayat"}
      <Riwayat />
    {:else}
      <Pengaturan />
    {/if}
  </main>
</div>

<Toasts />

<style>
  .shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  .sidebar {
    width: var(--sidebar-w);
    flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 16px 12px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 8px 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
  }
  .brand-mark {
    width: 36px;
    height: 36px;
    border-radius: 9px;
    background: var(--primary);
    color: #fff;
    font-weight: 800;
    font-size: 18px;
    display: grid;
    place-items: center;
  }
  .brand-name { font-weight: 700; font-size: 15px; }
  .brand-sub { font-size: 12px; color: var(--text-muted); }

  nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }
  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    border: none;
    background: transparent;
    padding: 10px 12px;
    border-radius: 8px;
    font-weight: 600;
    color: var(--text-muted);
    text-align: left;
  }
  .nav-item:hover { background: var(--primary-soft); color: var(--primary); }
  .nav-item.active { background: var(--primary); color: #fff; }
  .nav-icon { font-size: 16px; }

  .sidebar-foot {
    font-size: 11.5px;
    color: var(--text-muted);
    padding: 8px;
    text-align: center;
  }

  .content {
    flex: 1;
    overflow-y: auto;
    padding: 20px 24px;
  }
</style>
