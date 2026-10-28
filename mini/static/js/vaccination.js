/**
 * Smart Veterinary Clinic - Vaccination Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
  const vaccineSelect = document.getElementById('vaccineNameSelect');
  const adminDateInput = document.getElementById('administeredDateInput');
  const dueDateInput = document.getElementById('nextDueDateInput');

  if (vaccineSelect && adminDateInput && dueDateInput) {
    function recalculateDueDate() {
      if (!adminDateInput.value) return;

      const adminDate = new Date(adminDateInput.value);
      const selectedVaccine = vaccineSelect.value.toLowerCase();
      let monthsToAdd = 12; // Default 1 year

      if (selectedVaccine.includes('3-year') || selectedVaccine.includes('3 yr')) {
        monthsToAdd = 36;
      } else if (selectedVaccine.includes('6-month') || selectedVaccine.includes('puppy') || selectedVaccine.includes('kitten')) {
        monthsToAdd = 6;
      } else if (selectedVaccine.includes('booster')) {
        monthsToAdd = 12;
      }

      adminDate.setMonth(adminDate.getMonth() + monthsToAdd);
      dueDateInput.value = adminDate.toISOString().split('T')[0];
    }

    vaccineSelect.addEventListener('change', recalculateDueDate);
    adminDateInput.addEventListener('change', recalculateDueDate);
  }
});
