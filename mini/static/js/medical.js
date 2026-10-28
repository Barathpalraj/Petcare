/**
 * Smart Veterinary Clinic - Medical & Clinical Records Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
  // Dynamic Prescription Item Rows Builder
  const addPrescriptionItemBtn = document.getElementById('addPrescriptionItemBtn');
  const prescriptionItemsContainer = document.getElementById('prescriptionItemsContainer');

  if (addPrescriptionItemBtn && prescriptionItemsContainer) {
    addPrescriptionItemBtn.addEventListener('click', () => {
      const rowId = Date.now();
      const rowDiv = document.createElement('div');
      rowDiv.className = 'form-grid-3 prescription-row';
      rowDiv.id = `rx-row-${rowId}`;
      rowDiv.style.marginBottom = '1rem';
      rowDiv.innerHTML = `
        <div class="form-group">
          <label class="form-label">Medicine Name & Strength</label>
          <input type="text" name="medicine_name[]" class="form-control" placeholder="e.g. Amoxicillin 250mg" required>
        </div>
        <div class="form-group">
          <label class="form-label">Dosage & Frequency</label>
          <input type="text" name="dosage_freq[]" class="form-control" placeholder="e.g. 1 tab twice daily with food" required>
        </div>
        <div class="form-group" style="display: flex; gap: 0.5rem; align-items: flex-end;">
          <div style="flex: 1;">
            <label class="form-label">Duration</label>
            <input type="text" name="duration[]" class="form-control" placeholder="e.g. 7 days" required>
          </div>
          <button type="button" class="btn btn-danger btn-sm remove-rx-btn" style="height: 42px; width: 42px;" data-target="rx-row-${rowId}">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      `;

      prescriptionItemsContainer.appendChild(rowDiv);

      // Animate row entry
      if (typeof anime !== 'undefined') {
        anime({
          targets: rowDiv,
          translateY: [-10, 0],
          opacity: [0, 1],
          duration: 300,
          easing: 'easeOutQuad'
        });
      }

      // Bind remove button
      rowDiv.querySelector('.remove-rx-btn').addEventListener('click', function() {
        const target = document.getElementById(this.getAttribute('data-target'));
        if (target) target.remove();
      });
    });
  }
});
