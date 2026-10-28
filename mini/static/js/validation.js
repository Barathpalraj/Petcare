/**
 * Smart Veterinary Clinic - Form Validation
 * Real-time client-side inputs validator
 */

document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form[data-validate="true"]');

  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      let isValid = true;
      const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');

      requiredInputs.forEach(input => {
        if (!input.value.trim()) {
          isValid = false;
          input.classList.add('is-invalid');
          showInputError(input, 'This field is required');
        } else {
          input.classList.remove('is-invalid');
          clearInputError(input);

          // Email validation
          if (input.type === 'email' && !isValidEmail(input.value)) {
            isValid = false;
            input.classList.add('is-invalid');
            showInputError(input, 'Please enter a valid email address');
          }
        }
      });

      if (!isValid) {
        e.preventDefault();
        // Shake the submit button using Anime.js if available
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && typeof anime !== 'undefined') {
          anime({
            targets: submitBtn,
            translateX: [-10, 10, -8, 8, -4, 4, 0],
            duration: 450,
            easing: 'easeInOutSine'
          });
        }
      }
    });
  });

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function showInputError(input, msg) {
    let err = input.parentElement.querySelector('.form-error-msg');
    if (!err) {
      err = document.createElement('span');
      err.className = 'form-error-msg';
      err.style.color = '#ef4444';
      err.style.fontSize = '0.775rem';
      err.style.marginTop = '0.25rem';
      err.style.display = 'block';
      input.parentElement.appendChild(err);
    }
    err.innerText = msg;
  }

  function clearInputError(input) {
    const err = input.parentElement.querySelector('.form-error-msg');
    if (err) err.remove();
  }
});
