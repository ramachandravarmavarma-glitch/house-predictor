/**
 * static/js/main.js
 * Global interactive utilities, toast notifications, and modal controls for EstateAI
 */

function showNotification(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    `;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `flash-message flash-${type}`;
  toast.style.cssText = `
    min-width: 300px;
    max-width: 420px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    pointer-events: auto;
    animation: slideUpFade 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  `;

  let icon = 'fa-circle-info';
  if (type === 'success') icon = 'fa-circle-check';
  if (type === 'danger') icon = 'fa-triangle-exclamation';
  if (type === 'warning') icon = 'fa-circle-exclamation';

  toast.innerHTML = `
    <div style="display: flex; align-items: center; gap: 0.65rem;">
      <i class="fa-solid ${icon}"></i>
      <span style="font-weight: 500;">${message}</span>
    </div>
    <button type="button" style="background:none; border:none; color:inherit; cursor:pointer; margin-left: 0.75rem;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// Global keyboard listeners for closing active modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.estate-modal.active').forEach(modal => {
      modal.classList.remove('active');
    });
  }
});

// Close modal on backdrop click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('estate-modal')) {
    e.target.classList.remove('active');
  }
});
