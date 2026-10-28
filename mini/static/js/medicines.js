/**
 * Smart Veterinary Clinic - Pharmacy & Medicines
 */

document.addEventListener('DOMContentLoaded', () => {
  // Category filter
  const categorySelect = document.getElementById('medicineCategoryFilter');
  if (categorySelect) {
    categorySelect.addEventListener('change', () => {
      const selected = categorySelect.value.toLowerCase();
      const rows = document.querySelectorAll('.medicine-item-row');

      rows.forEach(row => {
        const cat = (row.getAttribute('data-category') || '').toLowerCase();
        if (!selected || cat === selected) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }

  // Highlight low stock rows
  const stockCells = document.querySelectorAll('.medicine-stock-cell');
  stockCells.forEach(cell => {
    const qty = parseInt(cell.getAttribute('data-qty') || '0', 10);
    const min = parseInt(cell.getAttribute('data-min') || '10', 10);

    if (qty <= min) {
      cell.innerHTML += ` <span class="badge badge-danger"><i class="fas fa-exclamation-triangle"></i> Low</span>`;
    }
  });
});
