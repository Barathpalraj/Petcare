/**
 * Smart Veterinary Clinic - Core Script
 * Micro-animations using Anime.js & Global UI Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Sidebar Drawer Toggle
  const sidebarToggle = document.getElementById('mobileSidebarToggle');
  const sidebar = document.getElementById('appSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-open');
      if (backdrop) backdrop.classList.toggle('active');
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', () => {
      if (sidebar) sidebar.classList.remove('sidebar-open');
      backdrop.classList.remove('active');
    });
  }

  // 2. Anime.js Entrance Animations for Cards and Sections
  if (typeof anime !== 'undefined') {
    // Staggered fade in & slide up for cards
    const animatedCards = document.querySelectorAll('.stat-card, .feature-card, .dashboard-card, .form-card, .table-wrapper');
    if (animatedCards.length > 0) {
      anime({
        targets: animatedCards,
        translateY: [20, 0],
        opacity: [0, 1],
        delay: anime.stagger(60, { start: 100 }),
        duration: 700,
        easing: 'easeOutQuart'
      });
    }

    // Hero title punchy animation
    const heroTitle = document.querySelector('.hero-content h1');
    if (heroTitle) {
      anime({
        targets: heroTitle,
        translateY: [-15, 0],
        opacity: [0, 1],
        duration: 900,
        easing: 'easeOutExpo'
      });
    }

    // Pulsing micro-animation for emergency and highlight badges
    anime({
      targets: '.badge-pulse',
      scale: [1, 1.06, 1],
      duration: 2000,
      loop: true,
      easing: 'easeInOutSine'
    });
  }

  // 3. Auto-dismiss Flash Toasts with Anime.js slide-out
  const toastElements = document.querySelectorAll('.flash-toast');
  toastElements.forEach(toast => {
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => dismissToast(toast));
    }

    // Auto dismiss after 5 seconds
    setTimeout(() => {
      dismissToast(toast);
    }, 5000);
  });

  function dismissToast(el) {
    if (!el) return;
    if (typeof anime !== 'undefined') {
      anime({
        targets: el,
        translateX: 120,
        opacity: 0,
        duration: 350,
        easing: 'easeInQuad',
        complete: () => el.remove()
      });
    } else {
      el.remove();
    }
  }

  // 4. Client-side Table Filter / Search
  const tableSearchInputs = document.querySelectorAll('.table-search-input');
  tableSearchInputs.forEach(input => {
    input.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const targetTableId = input.getAttribute('data-table-id') || 'dataTable';
      const targetTable = document.getElementById(targetTableId);
      if (!targetTable) return;

      const rows = targetTable.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (text.includes(query)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  });

  // 5. Image Dropzone Live Preview
  const fileInputs = document.querySelectorAll('input[type="file"].dropzone-input');
  fileInputs.forEach(input => {
    input.addEventListener('change', (e) => {
      const file = e.target.files[0];
      const previewBox = document.getElementById(input.getAttribute('data-preview-target') || 'imagePreview');
      const previewImg = document.getElementById(input.getAttribute('data-img-target') || 'previewImg');

      if (file && previewBox && previewImg) {
        const reader = new FileReader();
        reader.onload = (event) => {
          previewImg.src = event.target.result;
          previewBox.style.display = 'flex';
          if (typeof anime !== 'undefined') {
            anime({
              targets: previewBox,
              scale: [0.8, 1],
              opacity: [0, 1],
              duration: 400,
              easing: 'easeOutBack'
            });
          }
        };
        reader.readAsDataURL(file);
      }
    });
  });
});
