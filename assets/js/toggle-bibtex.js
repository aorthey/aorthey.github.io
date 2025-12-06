// Wait until the page is fully loaded
document.addEventListener('DOMContentLoaded', function () {
  // Find all buttons with class "toggle-bibtex"
  document.querySelectorAll('.toggle-bibtex').forEach(button => {
    button.addEventListener('click', () => {
      const targetId = button.getAttribute('data-target');
      const targetElement = document.getElementById(targetId);
      if (targetElement) {
        targetElement.classList.toggle('hidden');
      }
    });
  });
});

