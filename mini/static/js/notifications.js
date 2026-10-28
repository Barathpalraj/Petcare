/**
 * Smart Veterinary Clinic - Notifications Management
 */

document.addEventListener('DOMContentLoaded', () => {
  // Filter notifications by category
  const filterPills = document.querySelectorAll('.notification-filter-pill');
  const notificationItems = document.querySelectorAll('.notification-item-card');

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active', 'btn-primary'));
      filterPills.forEach(p => p.classList.add('btn-secondary'));
      pill.classList.remove('btn-secondary');
      pill.classList.add('active', 'btn-primary');

      const filterType = pill.getAttribute('data-filter');

      notificationItems.forEach(item => {
        const itemType = item.getAttribute('data-type');
        if (filterType === 'all' || itemType === filterType) {
          item.style.display = 'flex';
          if (typeof anime !== 'undefined') {
            anime({
              targets: item,
              opacity: [0, 1],
              translateY: [10, 0],
              duration: 300,
              easing: 'easeOutQuad'
            });
          }
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  // Mark notification as read with subtle fade
  const markReadButtons = document.querySelectorAll('.mark-read-btn');
  markReadButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      const card = this.closest('.notification-item-card');
      if (card) {
        card.classList.remove('unread');
        card.classList.add('read');
        this.remove();
      }
    });
  });
});
