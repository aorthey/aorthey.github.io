document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing copy buttons');
  const buttons = document.querySelectorAll('.copy-btn');
  console.log('Found', buttons.length, 'copy buttons');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const bibtex = button.getAttribute('data-bibtex');
      console.log('Attempting to copy:', bibtex);

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(bibtex).then(() => {
          console.log('Clipboard API success');
          button.textContent = 'Copied!';
          setTimeout(() => {
            button.textContent = 'Copy to Clipboard';
          }, 2000);
        }).catch(err => {
          console.error('Clipboard API failed:', err);
          fallbackCopy(bibtex, button);
        });
      } else {
        console.warn('Clipboard API not available, using fallback');
        fallbackCopy(bibtex, button);
      }
    });
  });
});

function fallbackCopy(text, button) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.select();
  try {
    document.execCommand('copy');
    console.log('Fallback copy success');
    button.textContent = 'Copied!';
    setTimeout(() => {
      button.textContent = 'Copy to Clipboard';
    }, 2000);
  } catch (err) {
    console.error('Fallback copy failed:', err);
  }
  document.body.removeChild(textArea);
}
