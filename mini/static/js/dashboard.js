/**
 * Smart Veterinary Clinic - Dashboard Scripts
 * Metric Counter Animation with Anime.js & Visual Charts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Animate KPI Stat numbers from 0 up to actual target
  if (typeof anime !== 'undefined') {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
      const text = stat.innerText.trim();
      const isCurrency = text.startsWith('₹');
      const cleanNum = parseFloat(text.replace(/[^0-9.-]+/g, '')) || 0;

      // Temporary object to animate property
      const counterObj = { count: 0 };
      anime({
        targets: counterObj,
        count: cleanNum,
        duration: 1200,
        easing: 'easeOutExpo',
        update: () => {
          if (isCurrency) {
            stat.innerText = '₹' + counterObj.count.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
          } else {
            stat.innerText = Math.round(counterObj.count).toLocaleString();
          }
        }
      });
    });

    // Animate progress bars or inventory levels
    const progressBars = document.querySelectorAll('.progress-bar-fill');
    if (progressBars.length > 0) {
      anime({
        targets: progressBars,
        width: (el) => el.getAttribute('data-percent') + '%',
        duration: 1000,
        delay: 300,
        easing: 'easeOutCubic'
      });
    }
  }

  // Quick action card hover bounce
  const quickActions = document.querySelectorAll('.quick-action-item');
  quickActions.forEach(item => {
    item.addEventListener('mouseenter', () => {
      if (typeof anime !== 'undefined') {
        anime({
          targets: item.querySelector('i'),
          scale: [1, 1.25, 1.1],
          duration: 300,
          easing: 'easeOutBack'
        });
      }
    });
  });
});
