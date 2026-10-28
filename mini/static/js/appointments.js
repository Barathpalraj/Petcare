/**
 * Smart Veterinary Clinic - Appointments Management
 */

document.addEventListener('DOMContentLoaded', () => {
  // Appointment status filter buttons
  const filterBtns = document.querySelectorAll('.appointment-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active', 'btn-primary'));
      filterBtns.forEach(b => b.classList.add('btn-secondary'));
      btn.classList.remove('btn-secondary');
      btn.classList.add('active', 'btn-primary');

      const status = btn.getAttribute('data-filter');
      const cards = document.querySelectorAll('.appointment-item-row');

      cards.forEach(card => {
        if (status === 'all' || card.getAttribute('data-status') === status) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // Time slot chips selection
  const timeSlots = document.querySelectorAll('.time-slot-chip');
  const selectedTimeInput = document.getElementById('appointmentTimeInput');

  timeSlots.forEach(slot => {
    slot.addEventListener('click', () => {
      timeSlots.forEach(s => s.classList.remove('selected'));
      slot.classList.add('selected');
      if (selectedTimeInput) {
        selectedTimeInput.value = slot.getAttribute('data-time') || slot.innerText.trim();
      }
    });
  });
});
