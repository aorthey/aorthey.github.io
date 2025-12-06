// copy-bibtex.js
const kTimeout = 2000;
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded – initializing BibTeX copy buttons');

  document.querySelectorAll('.copy-bibtex-button').forEach(button => {
    button.dataset.originalHtml = button.innerHTML;
    button.addEventListener('click', async () => {
      const container = button.closest('.bibtex-textfield');
      const oldText = button.innerHtml;
      const codeBlock = container?.querySelector('pre code');

      if (!codeBlock) {
        console.error('BibTeX code block not found');
        button.innerHtml = 'Error';
        setTimeout(() => {
          button.innerHTML = button.dataset.originalHtml;
        }, kTimeout);
        return;
      }

      const bibtexText = codeBlock.textContent.trim();

      if (!bibtexText) {
        button.innerHTML = "Empty";
        setTimeout(() => {
          button.innerHTML = button.dataset.originalHtml;
        }, kTimeout);
        return;
      }

      try {
        await navigator.clipboard.writeText(bibtexText);

        button.innerHTML = "Copied!";
        button.classList.add('copied');

        setTimeout(() => {
          button.innerHTML = button.dataset.originalHtml;
          button.classList.remove('copied');
        }, kTimeout);

      } catch (err) {
        console.error('Clipboard API failed:', err);
        fallbackCopy(bibtexText, button);
      }
    });
  });
});

function fallbackCopy(text, button) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();

  try {
    document.execCommand('copy');
    const oldText = button.textContent;
    button.textContent = 'Copied!';
    setTimeout(() => {
      button.innerHTML = button.dataset.originalHtml;
    }, kTimeout);
  } catch (err) {
    console.error('Fallback copy failed:', err);
    button.textContent = 'Failed';
  } finally {
    document.body.removeChild(textarea);
  }
}
