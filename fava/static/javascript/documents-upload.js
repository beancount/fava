import { $, $$, handleJSON } from './helpers';
import e from './events';

let dataTransferFiles = [];

e.on('form-submit-document-upload', (form) => {
  const promises = [];
  $$('#document-names input').forEach((element, index) => {
    const formData = new FormData(form);
    formData.append('file', dataTransferFiles[index], element.value);

    promises.push($.fetch(form.getAttribute('data-url'), {
      method: 'PUT',
      body: formData,
    })
      .then(handleJSON)
      .then((data) => {
        e.trigger('info', data.message);
      }, (error) => {
        e.trigger('error', `Upload error: ${error}`);
      }));
  });

  $('#documents-upload').classList.remove('shown');
  $('#document-names').innerHTML = '';
  dataTransferFiles = [];
  Promise.all(promises)
    .then(() => {
      e.trigger('reload');
    });
});

// File uploads via Drag and Drop on elements with class "droptarget" and
// attribute "data-account-name"
e.on('page-loaded', () => {
  $$('.droptarget').forEach((target) => {
    target.addEventListener('dragenter', (event) => {
      target.classList.add('dragover');
      event.preventDefault();
      event.stopPropagation();
    });

    target.addEventListener('dragover', (event) => {
      target.classList.add('dragover');
      event.preventDefault();
      event.stopPropagation();
    });

    target.addEventListener('dragleave', (event) => {
      target.classList.remove('dragover');
      event.preventDefault();
      event.stopPropagation();
    });

    target.addEventListener('drop', (event) => {
      target.classList.remove('dragover');
      event.preventDefault();
      event.stopPropagation();

      dataTransferFiles = event.dataTransfer.files;
      const form = $('#document-upload-form');
      const dateAttribute = target.getAttribute('data-entry-date');
      const entryDate = dateAttribute || new Date().toISOString().substring(0, 10);
      form.elements.account.value = target.getAttribute('data-account-name');
      form.elements.hash.value = target.getAttribute('data-entry');

      let changedFilename = false;

      if (!form.elements.folder.length) {
        e.trigger('error', 'You need to set the "documents" Beancount option for file uploads.');
        return;
      }

      // add input elements for files
      $('#document-names').innerHTML = '';
      for (let i = 0; i < dataTransferFiles.length; i += 1) {
        let filename = dataTransferFiles[i].name;

        if (!/^\d{4}-\d{2}-\d{2}/.test(filename)) {
          filename = `${entryDate} ${filename}`;
          changedFilename = true;
        }

        $('#document-names').insertAdjacentHTML('beforeend', `<input value="${filename}">`);
      }

      if (form.elements.folder.length > 1 || changedFilename) {
        $('#documents-upload').classList.add('shown');
        $('#document-names input').focus();
      } else {
        e.trigger('form-submit-document-upload', form);
      }
    });
  });
});
