import type {  Layout, PlotData } from 'plotly.js';

export interface Dataset {
    index: string[];
    observation: number[];
    simulation: number[];
}

interface Plot {
    data: Partial<PlotData>[]
    layout: Partial<Layout>
}

export function createTimeseriesPlot(name: string,dataset: Dataset): Plot {
    return {
        data: [
            {  
                type: 'scatter',
                x: dataset.index,
                y: dataset.observation,
                mode: 'lines',
                name: 'Observed',
                line: { color: '#1f77b4' }
            },
            {
                type: 'scatter',
                x: dataset.index,
                y: dataset.simulation,
                mode: 'lines',
                name: 'Simulated',
                line: { color: '#ff7f0e', dash: 'dash' }
            }
        ],
        layout: {
            title: {
                text: `Time Series - ${name}`,
                font: {
                    size: 20
                }
            },
            xaxis: {
                tickangle: 45,
                autorange: true,
                rangeslider: {
                    range: [dataset.index[0], dataset.index[Math.floor(dataset.index.length / 10) + 1]]
                },
                type: 'date'
            },
            legend: {
                orientation: 'h',
                y: 1.02,
                x: 1,
                yanchor: 'bottom',
                xanchor: 'right'
            }
        }
    }
}

export function create2dDensityPlot(name: string, dataset: Dataset): Plot {
    return {
        data: [
            {
                mode: 'markers',
                x: dataset.observation,
                y: dataset.simulation,
                type: 'scatter',
                marker: {
                    color: 'rgb(102,0,0)',
                    size: 2,
                    opacity: 0.4
                },
                name: 'Obs - Sim'
            },
            {
                type: 'histogram2dcontour',
                x: dataset.observation,
                y: dataset.simulation,
                ncontours: 20,
                colorscale: 'Hot',
                showscale: false,
                reversescale: true,
                name: 'Density'
            },
            {
                type: 'histogram',
                x: dataset.observation,
                marker: {
                    color: 'rgb(102,0,0)',
                },
                yaxis: 'y2',
                name: 'Observation Histogram'
            },
            {
                type: 'histogram',
                y: dataset.simulation,
                marker: {
                    color: 'rgb(102,0,0)',
                },
                xaxis: 'x2',
                name: 'Simulation Histogram'
            }
        ],
        layout: {
            showlegend: false,
            margin: {t: 50},
            hovermode: 'closest',
            bargap: 0,
            xaxis: {
                domain: [0, 0.85],
                showgrid: false,
                zeroline: false,
            },
            yaxis: {
                domain: [0, 0.85],
                showgrid: false,
                zeroline: false,
            },
            xaxis2: {
                domain: [0.85, 1],
                showgrid: false,
                zeroline: false,
            },
            yaxis2: {
                domain: [0.85, 1],
                showgrid: false,
                zeroline: false,
            }
        }
    }
}

export function createParallelCoordinatesPlot(metrics: Array<Record<string, number | string>>): Plot {
    const metricNames: string[] = [];
    const firstMetric = metrics[0];
    if (firstMetric) {
        Object.keys(firstMetric).forEach(key => {
            if (key !== 'Catchment' && typeof firstMetric[key] === 'number') {
                metricNames.push(key);
            }
        });
    }
    const dimensions = metricNames.map(metricName => {
        const values = metrics.map(m => {
            const val = m[metricName];
            return typeof val === 'number' ? val : null;
        });
        
        // Calculate range for this metric (only from valid numbers)
        const validValues = values.filter((v): v is number => v !== null);
        const min = validValues.length > 0 ? Math.min(...validValues) : 0;
        const max = validValues.length > 0 ? Math.max(...validValues) : 1;
        
        return {
            label: metricName,
            values: values,
            range: [min, max],
            tickformat: '.4f'
        };
    });
    
    const colorValues = metrics.map(m => {
        const val = m[metricNames[0]];
        return typeof val === 'number' ? val : 0;
    });
    
    return {
        data: [{
            type: 'parcoords',
            dimensions: dimensions,
            line: {
                color: colorValues,
                colorscale: 'Viridis',
                showscale: true,
                colorbar: {
                    title: {
                        text: metricNames[0] || 'Metric'
                    }
                }
            } as any,
            labelfont: {
                size: 12
            },
            tickfont: {
                size: 10
            }
        } as Partial<PlotData>],
        layout: {
            title: {
                text: 'Metrics Comparison Across Catchments',
                font: {
                    size: 20
                }
            },
            margin: {
                l: 80,
                r: 80,
                t: 80,
                b: 80
            }
        }
    };
}

export function createHistogramPlot(name: string, dataset: Dataset): Plot {
    return {
        data: [
            {
                type: 'histogram',
                x: dataset.observation,
                name: 'Observed',
                marker: {
                    color: '#1f77b4',
                    opacity: 0.7
                },
                histnorm: 'probability density',
                nbinsx: 50
            } as Partial<PlotData>,
            {
                type: 'histogram',
                x: dataset.simulation,
                name: 'Simulated',
                marker: {
                    color: '#ff7f0e',
                    opacity: 0.7
                },
                histnorm: 'probability density',
                nbinsx: 50
            } as Partial<PlotData>
        ],
        layout: {
            title: {
                text: `Distribution - ${name}`,
                font: {
                    size: 20
                }
            },
            xaxis: {
                title: {
                    text: 'Value'
                }
            },
            yaxis: {
                title: {
                    text: 'Probability Density'
                }
            },
            barmode: 'overlay',
            legend: {
                orientation: 'h',
                y: 1.02,
                x: 1,
                yanchor: 'bottom',
                xanchor: 'right'
            }
        }
    };
}
