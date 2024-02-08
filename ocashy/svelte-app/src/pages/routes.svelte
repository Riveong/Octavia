<script>
    import { onMount, onDestroy } from 'svelte';
    import Table from '../components/table.svelte';
    import PdfTable from '../components/pdf-table.svelte';
    import Cashier from '../components/cashier.svelte';
    import Help from '../components/help.svelte';
    import Edit from '../components/edit.svelte';


    let currentRoute = '';

    function hashChange() {
        currentRoute = window.location.hash;
    }

    onMount(() => {
        window.addEventListener('hashchange', hashChange);
        hashChange(); // Initialize route on page load
    });

    onDestroy(() => {
        window.removeEventListener('hashchange', hashChange);
    });
</script>

{#if currentRoute === '#categories'}
    <Table />
{:else if currentRoute === '#files'}
    <PdfTable />
{:else if currentRoute === '#cashier'}
    <Cashier />
{:else if currentRoute === '#edit'}
    <Edit />
{:else if currentRoute === '#help'}
    <Help />
{:else}
    <Table /> <!-- Default route -->
{/if}
