<script module lang="ts">
  // Declare pako and Plotly as globals from script tags
  declare const pako: any;
  declare const Plotly: any;
  import { createTimeseriesPlot, create2dDensityPlot, createHistogramPlot, createParallelCoordinatesPlot, type Dataset } from '$lib/plots';
</script>

<script lang="ts">
  import { names, metrics, datasetCompressed } from '$lib/index.js';
  import { config } from '$lib/config.js';



  let selectedName = $state(names?.[0] ?? '');
  let chartElement = $state<HTMLDivElement | null>(null);
  let activeTab = $state<'timeseries' | 'density' | 'histogram'>('timeseries');
  let activeMetricsTab = $state<'table' | 'parallel'>('table');
  
  // Decompressed datasets
  let datasets = $state<Record<string, Dataset> | null>(null);
  
  // Separate chart element for parallel coordinates plot
  let parallelCoordsElement = $state<HTMLDivElement | null>(null);

  // Decompress dataset on load
  $effect(() => {
    if (!datasetCompressed || datasets !== null) return;
    
    try {
      // 1. Decode base64
      const binaryString = atob(datasetCompressed);
      
      // 2. Convert to Uint8Array for pako
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // 3. Decompress with pako
      const decompressed = pako.inflate(bytes, { to: 'string' });
      
      // 4. Parse JSON
      datasets = JSON.parse(decompressed);
      
      // 5. Console.log the decompressed data
      console.log('Decompressed datasets:', datasets);
    } catch (error) {
      console.error('Error decompressing dataset:', error);
    }
  });

  // Plotly is loaded from CDN as global variable

  

  // Generate plot from current dataset based on active tab
  let currentPlot = $derived.by(() => {
    if (!selectedName || !datasets || !datasets[selectedName]) return null;
    
    if (activeTab === 'timeseries') {
      return createTimeseriesPlot(selectedName, datasets[selectedName]);
    } else if (activeTab === 'density') {
      return create2dDensityPlot(selectedName, datasets[selectedName]);
    } else if (activeTab === 'histogram') {
      return createHistogramPlot(selectedName, datasets[selectedName]);
    }
    return null;
  });
  
  // Generate parallel coordinates plot (uses all metrics, not catchment-specific)
  let parallelCoordsPlot = $derived.by(() => {
    // Convert metrics object to array format
    const metricsArray = Object.entries(metrics).map(([catchment, metricValues]) => ({
      Catchment: catchment,
      ...metricValues
    }));
    return createParallelCoordinatesPlot(metricsArray);
  });

  // Render/resize plot for chart section
  $effect(() => {
    if (!chartElement || !currentPlot || typeof Plotly === 'undefined') return;

    Plotly.react(
      chartElement,
      currentPlot.data,
      currentPlot.layout,
      { responsive: true, displayModeBar: false }
    );

    const onResize = () => {
      if (typeof Plotly !== 'undefined' && chartElement) {
        Plotly.Plots.resize(chartElement);
      }
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  });
  
  // Render/resize parallel coordinates plot
  $effect(() => {
    if (!parallelCoordsElement || !parallelCoordsPlot || typeof Plotly === 'undefined') return;

    Plotly.react(
      parallelCoordsElement,
      parallelCoordsPlot.data,
      parallelCoordsPlot.layout,
      { responsive: true, displayModeBar: false }
    );

    const onResize = () => {
      if (typeof Plotly !== 'undefined' && parallelCoordsElement) {
        Plotly.Plots.resize(parallelCoordsElement);
      }
    };
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

    <!-- Tabs -->
    <div class="mb-4 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          type="button"
          class="whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors {activeTab === 'timeseries' 
            ? 'border-indigo-500 text-indigo-600' 
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
          onclick={() => activeTab = 'timeseries'}
        >
          Time Series
        </button>
        <button
          type="button"
          class="whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors {activeTab === 'density' 
            ? 'border-indigo-500 text-indigo-600' 
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
          onclick={() => activeTab = 'density'}
        >
          Density Plot
        </button>
        <button
          type="button"
          class="whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors {activeTab === 'histogram' 
            ? 'border-indigo-500 text-indigo-600' 
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
          onclick={() => activeTab = 'histogram'}
        >
          Histogram
        </button>
      </nav>
    </div>

    <!-- Chart Content -->
    <!-- All chart tabs (timeseries, density, histogram) need selectedName and datasets -->
    {#if !selectedName}
      <div class="text-gray-500">No selection.</div>
    {:else if !datasets}
      <div class="w-full h-[450px] bg-gray-100 rounded-lg grid place-items-center">
        <span class="text-gray-500 text-sm">Loading dataset…</span>
      </div>
    {:else if typeof Plotly === 'undefined'}
      <div class="w-full h-[450px] bg-gray-100 rounded-lg grid place-items-center">
        <span class="text-gray-500 text-sm">Loading Plotly…</span>
      </div>
    {:else if !currentPlot}
      <div class="w-full h-[450px] bg-gray-100 rounded-lg grid place-items-center">
        <span class="text-gray-500 text-sm">No data available for {selectedName}</span>
      </div>
    {:else}
      <div bind:this={chartElement} class="w-full h-[450px] bg-gray-200 rounded-lg overflow-hidden"></div>
    {/if}
  </section>

  <section id="metrics" class="mb-12">
    <h2 class="text-xl font-semibold mb-4">Performance Metrics</h2>

    <!-- Metrics Tabs -->
    <div class="mb-4 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Metrics Tabs">
        <button
          type="button"
          class="whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors {activeMetricsTab === 'table' 
            ? 'border-indigo-500 text-indigo-600' 
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
          onclick={() => activeMetricsTab = 'table'}
        >
          Metrics Table
        </button>
        <button
          type="button"
          class="whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors {activeMetricsTab === 'parallel' 
            ? 'border-indigo-500 text-indigo-600' 
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}"
          onclick={() => activeMetricsTab = 'parallel'}
        >
          Parallel Coordinates
        </button>
      </nav>
    </div>

    <!-- Metrics Content -->
    {#if activeMetricsTab === 'table'}
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
    {:else}
      <!-- Parallel Coordinates Plot -->
      {#if typeof Plotly === 'undefined'}
        <div class="w-full h-[450px] bg-gray-100 rounded-lg grid place-items-center">
          <span class="text-gray-500 text-sm">Loading Plotly…</span>
        </div>
      {:else if !parallelCoordsPlot}
        <div class="w-full h-[450px] bg-gray-100 rounded-lg grid place-items-center">
          <span class="text-gray-500 text-sm">No metrics data available</span>
        </div>
      {:else}
        <div bind:this={parallelCoordsElement} class="w-full h-[450px] bg-gray-200 rounded-lg overflow-hidden"></div>
      {/if}
    {/if}
  </section>
</div>
