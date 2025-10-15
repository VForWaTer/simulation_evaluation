<script>
  import { names, metrics } from '$lib/report_data.js';
  import { config } from '$lib/config.js';
  import { plotIndex } from '$lib/plot_index.js';

  let selectedName = $state(names?.[0] ?? '');
  let chartElement = $state(null);        

  const plotCache = new Map();
  let PlotlyLib = $state(null);

  // load Plotly once
  $effect(async () => {
    if (!PlotlyLib) {
      const mod = await import('plotly.js-dist-min');
      PlotlyLib = mod.default ?? mod;
    }
  });

  // ensure selected plot is cached
  $effect(async () => {
    if (!selectedName) return;
    if (!plotCache.has(selectedName)) {
      const url = plotIndex[selectedName];
      if (!url) return;
      const res = await fetch(url);
      const fig = await res.json();
      plotCache.set(selectedName, fig);
    }
  });

  let currentPlot = $derived(plotCache.get(selectedName));

  // render/resize
  $effect(() => {
    if (!chartElement || !currentPlot || !PlotlyLib) return;

    PlotlyLib.react(
      chartElement,
      currentPlot.data ?? currentPlot,
      currentPlot.layout ?? { title: selectedName },
      { responsive: true, displayModeBar: false }
    );

    const onResize = () => PlotlyLib.Plots.resize(chartElement);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  });
</script>

<div class="container mx-auto px-4 py-8">
  <header class="bg-white shadow-sm mb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-semibold text-gray-900">{config.title}</h1>
          <select
            bind:value={selectedName}
            class="block w-56 rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
          >
            {#each names as name}
              <option value={name}>{name}</option>
            {/each}
          </select>
        </div>
        <nav class="flex space-x-4">
          <a href="#chart" class="text-gray-600 hover:text-gray-900">Chart</a>
          <a href="#metrics" class="text-gray-600 hover:text-gray-900">Metrics</a>
        </nav>
      </div>
    </div>
  </header>

  <section id="chart" class="mb-12">
    <h2 class="text-xl font-semibold mb-4">Performance Chart</h2>

    {#if !selectedName}
      <div class="text-gray-500">No selection.</div>
    {:else if !PlotlyLib || !currentPlot}
      <div class="w-full h-[450px] bg-gray-100 rounded-lg grid place-items-center">
        <span class="text-gray-500 text-sm">Loading plot…</span>
      </div>
    {:else}
      <div bind:this={chartElement} class="w-full h-[450px] bg-gray-200 rounded-lg overflow-hidden"></div>
    {/if}
  </section>

  <section id="metrics" class="mb-12">
    <h2 class="text-xl font-semibold mb-4">Performance Metrics</h2>
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Catchment</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">NSE</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">KGE</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">R²</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MSE</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RMSE</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each Object.entries(metrics) as [catchment, metric]}
            <tr
                class="cursor-pointer hover:bg-gray-50 {catchment === selectedName ? 'bg-indigo-50' : ''}"
                onclick={() => (selectedName = catchment)}
                >
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{catchment}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{metric.NSE.toFixed(4)}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{metric.KGE.toFixed(4)}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{metric['R²'].toFixed(4)}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{metric.MSE.toFixed(4)}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{metric.RMSE.toFixed(4)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>
</div>
