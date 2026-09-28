/**
 * static/js/dataset.js
 * Client-side asynchronous pagination and search handler for EstateAI dataset explorer
 */

let currentPage = 1;
let totalPages = 1;
let currentSearch = '';
let searchTimeout = null;

function fetchDatasetRows(page = 1, search = '') {
  const url = `/api/dataset/rows?page=${page}&per_page=12&search=${encodeURIComponent(search)}`;
  
  fetch(url)
    .then(r => r.json())
    .then(res => {
      if (!res.success) return;
      const data = res.data;
      currentPage = data.page;
      totalPages = data.total_pages;
      currentSearch = search;

      renderDatasetTable(data.records);
      updatePaginationControls(data);
    })
    .catch(err => {
      console.error("Error fetching dataset page:", err);
    });
}

function renderDatasetTable(records) {
  const tbody = document.getElementById('datasetTableBody');
  if (!tbody) return;

  if (!records || records.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="11" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          No matching records found.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = records.map(r => `
    <tr>
      <td><strong style="color: #34d399;">${r.formatted_price}</strong></td>
      <td><strong style="color: #ffffff;">${r.location}</strong></td>
      <td>${r.area}</td>
      <td>${r.bedrooms}</td>
      <td>${r.bathrooms}</td>
      <td>${r.floors}</td>
      <td>${r.parking}</td>
      <td><span class="badge-status ready" style="font-size: 0.7rem;">${r.furnishing_status}</span></td>
      <td style="text-transform: capitalize;">${r.main_road}</td>
      <td style="text-transform: capitalize;">${r.air_conditioning}</td>
      <td style="text-transform: capitalize;">${r.preferred_area}</td>
    </tr>
  `).join('');
}

function updatePaginationControls(data) {
  const curPageEl = document.getElementById('curPageNum');
  const totalPageEl = document.getElementById('totalPageNum');
  const infoEl = document.getElementById('paginationInfo');
  const prevBtn = document.getElementById('btnPrevPage');
  const nextBtn = document.getElementById('btnNextPage');

  if (curPageEl) curPageEl.innerText = data.page;
  if (totalPageEl) totalPageEl.innerText = data.total_pages;
  if (infoEl) {
    infoEl.innerHTML = `Showing Page <strong id="curPageNum">${data.page}</strong> of <strong id="totalPageNum">${data.total_pages}</strong> (${data.total_records} records)`;
  }

  if (prevBtn) prevBtn.disabled = data.page <= 1;
  if (nextBtn) nextBtn.disabled = data.page >= data.total_pages;
}

function changeDatasetPage(delta) {
  const targetPage = currentPage + delta;
  if (targetPage >= 1 && targetPage <= totalPages) {
    fetchDatasetRows(targetPage, currentSearch);
  }
}

function handleDatasetSearch() {
  const val = document.getElementById('datasetSearchInput').value.trim();
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchDatasetRows(1, val);
  }, 300);
}

function clearDatasetSearch() {
  const input = document.getElementById('datasetSearchInput');
  if (input) {
    input.value = '';
    fetchDatasetRows(1, '');
  }
}
