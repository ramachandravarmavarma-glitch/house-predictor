/**
 * static/js/charts.js
 * Chart.js configurations and rendering logic for EstateAI analytics dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/analytics/charts')
    .then(r => r.json())
    .then(res => {
      if (!res.success) return;
      const data = res.charts;

      renderPriceDistribution(data.price_bins);
      renderAreaVsPrice(data.area_vs_price);
      renderBedroomsVsPrice(data.bedrooms_vs_price);
      renderLocationVsPrice(data.location_vs_price);
      renderFurnishingVsPrice(data.furnishing_vs_price);
      renderHoldoutActualVsPredicted(data.actual_vs_predicted);
    })
    .catch(err => console.error("Error loading analytics charts:", err));
});

function formatLakhs(val) {
  return `₹${(val / 100000).toFixed(1)}L`;
}

function renderPriceDistribution(bins) {
  const canvas = document.getElementById('priceDistributionChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(99, 102, 241, 0.85)');
  gradient.addColorStop(1, 'rgba(6, 182, 212, 0.15)');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: bins.labels.map(l => l.replace('₹', '').replace(/,/g, '')),
      datasets: [{
        label: 'Properties in Range',
        data: bins.counts,
        backgroundColor: gradient,
        borderColor: '#6366f1',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.raw} properties`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#64748b', maxRotation: 45, minRotation: 45, font: { size: 10 } },
          grid: { display: false }
        },
        y: {
          title: { display: true, text: 'Property Count', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}

function renderAreaVsPrice(points) {
  const canvas = document.getElementById('areaVsPriceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const scatterData = points.map(p => ({ x: p.x, y: p.y / 100000, loc: p.location }));

  new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Area vs Price',
        data: scatterData,
        backgroundColor: 'rgba(6, 182, 212, 0.75)',
        borderColor: '#06b6d4',
        borderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.raw.loc}: ${ctx.raw.x} sqft -> ₹${ctx.raw.y.toFixed(1)} Lakhs`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Area (sq ft)', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
          title: { display: true, text: 'Price (₹ Lakhs)', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}

function renderBedroomsVsPrice(data) {
  const canvas = document.getElementById('bedroomsVsPriceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Average Price (₹ Lakhs)',
        data: data.values.map(v => v / 100000),
        backgroundColor: 'rgba(56, 189, 248, 0.65)',
        borderColor: '#38bdf8',
        borderWidth: 1,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Avg Price: ₹${ctx.raw.toFixed(2)} Lakhs`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8' },
          grid: { display: false }
        },
        y: {
          title: { display: true, text: 'Price (₹ Lakhs)', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}

function renderLocationVsPrice(data) {
  const canvas = document.getElementById('locationVsPriceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Avg Price (₹ Lakhs)',
        data: data.values.map(v => v / 100000),
        backgroundColor: 'rgba(139, 92, 246, 0.7)',
        borderColor: '#8b5cf6',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Avg Valuation: ₹${ctx.raw.toFixed(2)} Lakhs`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Price (₹ Lakhs)', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
          ticks: { color: '#94a3b8', font: { size: 10 } },
          grid: { display: false }
        }
      }
    }
  });
}

function renderFurnishingVsPrice(data) {
  const canvas = document.getElementById('furnishingVsPriceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.values.map(v => v / 100000),
        backgroundColor: [
          'rgba(16, 185, 129, 0.75)',
          'rgba(6, 182, 212, 0.75)',
          'rgba(244, 63, 94, 0.75)'
        ],
        borderColor: '#0f172a',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#94a3b8', font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: Avg ₹${ctx.raw.toFixed(2)} Lakhs`
          }
        }
      }
    }
  });
}

function renderHoldoutActualVsPredicted(samples) {
  const canvas = document.getElementById('analyticsActualPredictedChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const scatterData = (samples || []).map(s => ({
    x: s.actual / 100000,
    y: s.predicted / 100000
  }));

  const allVals = (samples || []).flatMap(s => [s.actual / 100000, s.predicted / 100000]);
  const minVal = allVals.length ? Math.floor(Math.min(...allVals) * 0.9) : 0;
  const maxVal = allVals.length ? Math.ceil(Math.max(...allVals) * 1.1) : 500;

  new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Prediction Samples',
          data: scatterData,
          backgroundColor: 'rgba(16, 185, 129, 0.75)',
          borderColor: '#10b981',
          pointRadius: 4
        },
        {
          type: 'line',
          label: 'Fit Baseline',
          data: [{ x: minVal, y: minVal }, { x: maxVal, y: maxVal }],
          borderColor: '#fb7185',
          borderDash: [5, 5],
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          title: { display: true, text: 'Actual (₹ Lakhs)', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        },
        y: {
          title: { display: true, text: 'Predicted (₹ Lakhs)', color: '#94a3b8' },
          ticks: { color: '#64748b' },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}
