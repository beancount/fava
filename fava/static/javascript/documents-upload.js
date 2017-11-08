import { $, $$, handleJSON } from './helpers';
import e from './events';

const filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}$/;

function uploadDocument(formData) {
  const documentFolder = $('#document-upload-folder').value;
  formData.append('folder', documentFolder);

  $.fetch($('#document-upload-submit').getAttribute('data-url'), {
    method: 'PUT',
    body: formData,
  })
    .then(handleJSON)
    .then((data) => {
      e.trigger('info', data.message);
    }, (error) => {
      e.trigger('error', `Upload error: ${error}`);
    });
}

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

      const folders = $$('#document-upload-folder option');
      const { files } = event.dataTransfer;
      let entryDate = new Date();
      const entryDateString = target.getAttribute('data-entry-date');
      if (entryDateString) {
        entryDate = new Date(entryDateString);
      }
      let changedFilename = false;

      if (!folders.length) {
        e.trigger('error', 'You need to set the "documents" Beancount option to enable file uploads.');
        return;
      }

      // add input elements for files
      $('#document-names').innerHTML = '';
      for (let i = 0; i < files.length; i += 1) {
        let filename = files[i].name;

        if (filename.length < 11 || filenameRegex.test(filename.substring(0, 10)) === false) {
          filename = `${entryDate.toISOString().substring(0, 10)} ${filename}`;
          changedFilename = true;
        }

        $('#document-names').insertAdjacentHTML('beforeend', `<input type="text" value="${filename}" data-index="${i}">`);
      }

      // upload files on submit
      $.once($('#document-upload-submit'), 'click', (event_) => {
        event_.preventDefault();

        $$('#document-names input').forEach((element) => {
          const formData = new FormData();
          const file = files[element.getAttribute('data-index')];
          const accountName = target.getAttribute('data-account-name');
          const entryHash = target.getAttribute('data-entry');
          formData.append('file', file, element.value);
          formData.append('account', accountName);

          if (entryHash) {
            // statement upload (add adding it to metadata)
            formData.append('entry_hash', entryHash);
          }

          uploadDocument(formData);
        });

        $('#documents-upload').classList.remove('shown');
        $('#document-names').innerHTML = '';
        e.trigger('reload');
      });

      if (folders.length > 1 || changedFilename) {
        $('#documents-upload').classList.add('shown');
      } else {
        $('#document-upload-submit').click();
      }
    });
  });
});
