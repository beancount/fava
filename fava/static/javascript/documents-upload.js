import { $, $$, handleJSON } from './helpers';
import e from './events';

const filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}$/;

function uploadDocument(formData) {
  const documentFolderIndex = $('#document-upload-folder').value;
  formData.append('targetFolderIndex', documentFolderIndex);

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
export default function initDocumentsUpload() {
  $$('.droptarget').forEach((target) => {
    target.addEventListener('dragenter', (event) => {
      target.classList.add('dragover');
      event.preventDefault();
    });

    target.addEventListener('dragover', (event) => {
      target.classList.add('dragover');
      event.preventDefault();
    });

    target.addEventListener('dragleave', (event) => {
      target.classList.remove('dragover');
      event.preventDefault();
    });

    target.addEventListener('drop', (event) => {
      target.classList.remove('dragover');
      event.preventDefault();

      const accountName = target.getAttribute('data-account-name');
      const folders = $$('#document-upload-folder option');
      const files = event.dataTransfer.files;
      const now = new Date();
      let changedFilename = false;

      const bfilename = target.getAttribute('data-filename')
      const blineno = target.getAttribute('data-lineno')

      if (!folders.length) {
        e.trigger('error', 'You need to set the "documents" Beancount option to enable file uploads.');
        return;
      }

      // add input elements for files
      for (let i = 0; i < files.length; i += 1) {
        let filename = files[i].name;

        if (filename.length < 11 || filenameRegex.test(filename.substring(0, 10)) === false) {
          filename = `${now.toISOString().substring(0, 10)} ${filename}`;
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
          formData.append('file', file);
          formData.append('account', accountName);
          formData.append('filename', element.value);

          if (bfilename) {  // statement upload (add adding it to metadata)
            formData.append('bfilename', bfilename);
            formData.append('blineno', blineno);
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
}
