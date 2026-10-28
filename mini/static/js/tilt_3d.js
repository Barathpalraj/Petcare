/**
 * Smart Veterinary Clinic - Professional 3D Perspective Tilt Engine
 * True 3D raycasting, multi-layer Z-depth, and dynamic specular sheen
 */

(function () {
  'use strict';

  function init3DTilt() {
    const cards = document.querySelectorAll('.tilt-card');

    cards.forEach((card) => {
      // Create glare highlight element if not exists
      let glare = card.querySelector('.tilt-glare');
      if (!glare) {
        glare = document.createElement('div');
        glare.className = 'tilt-glare';
        card.appendChild(glare);
      }

      card.addEventListener('mouseenter', () => {
        card.style.transition = 'transform 0.15s ease-out, box-shadow 0.15s ease-out';
      });

      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const cardWidth = rect.width;
        const cardHeight = rect.height;

        const centerX = rect.left + cardWidth / 2;
        const centerY = rect.top + cardHeight / 2;

        const mouseX = e.clientX - centerX;
        const mouseY = e.clientY - centerY;

        const maxTilt = parseFloat(card.getAttribute('data-tilt-max') || '14');
        const rotateX = -((mouseY / (cardHeight / 2)) * maxTilt).toFixed(2);
        const rotateY = ((mouseX / (cardWidth / 2)) * maxTilt).toFixed(2);

        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.03, 1.03, 1.03)`;
        card.style.boxShadow = `${-rotateY * 1.5}px ${rotateX * 1.5 + 15}px 35px rgba(13, 148, 136, 0.18), 0 20px 25px -5px rgba(15, 23, 42, 0.12)`;

        // Specular Glare Movement
        const glareX = ((e.clientX - rect.left) / cardWidth) * 100;
        const glareY = ((e.clientY - rect.top) / cardHeight) * 100;
        glare.style.background = `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255, 255, 255, 0.45) 0%, rgba(255, 255, 255, 0) 65%)`;
        glare.style.opacity = '1';
      });

      card.addEventListener('mouseleave', () => {
        card.style.transition = 'transform 0.6s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.6s ease';
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        card.style.boxShadow = '';
        if (glare) {
          glare.style.opacity = '0';
        }
      });
    });
  }

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init3DTilt);
  } else {
    init3DTilt();
  }

  window.init3DTilt = init3DTilt;
})();
