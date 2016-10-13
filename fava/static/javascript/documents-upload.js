const Backbone = require('backbone');

const filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}$/;

function uploadDocument(formData, filename) {
  const documentFolderIndex = $('#document-upload-folder').val();

  formData.append('filename', filename);
  formData.append('targetFolderIndex', documentFolderIndex);

  $.ajax({
    type: 'PUT',
    url: $('#document-upload-submit').data('url'),
    data: formData,
    contentType: false,
    processData: false,
    success(data) {
      if (data.success) {
        Backbone.trigger('info', data.message);
      } else {
        Backbone.trigger('error', `Upload error: ${data.error}`);
      }
    },
    error() {
      Backbone.trigger('error', 'Unknown upload error');
    },
  });
}

// File uploads via Drag and Drop on elements with class "droptarget" and
// attribute "data-account-name"
module.exports.initDocumentsUpload = function initDocumentsUpload() {
  $('.droptarget').on('dragenter dragover', (event) => {
    $(event.currentTarget).addClass('dragover');
    event.preventDefault();
  });

  $('.droptarget').on('dragleave', (event) => {
    $(event.currentTarget).removeClass('dragover');
    event.preventDefault();
  });

  $('.droptarget').on('drop', (event) => {
    $(event.currentTarget).removeClass('dragover');
    event.preventDefault();

    const accountName = $(event.currentTarget).data('account-name');
    const folders = $('#document-upload-folder option');
    const files = event.originalEvent.dataTransfer.files;
    const now = new Date();
    let changedFilename = false;

    if (!folders.length) {
      Backbone.trigger('error', 'You need to set the "documents" Beancount option to enable file uploads.');
      return;
    }

    // add input elements for files
    for (let i = 0; i < files.length; i += 1) {
      let filename = files[i].name;

      if (filename.length < 11 || filenameRegex.test(filename.substring(0, 10)) === false) {
        filename = `${now.toISOString().substring(0, 10)} ${filename}`;
        changedFilename = true;
      }

      $('#document-names').append(`<input type="text" value="${filename}" data-index="${i}">`);
    }

    // upload files on submit
    $('#document-upload-submit').one('click', (event) => {
      event.preventDefault();

      $('#document-names input').each((index, element) => {
        const formData = new FormData();
        const file = files[$(element).data('index')];
        formData.append('file', file);
        formData.append('account_name', accountName);

        uploadDocument(formData, $(element).val());
      });

      $('#documents-upload').removeClass('shown');
      $('#document-names').empty();
    });

    if (folders.length > 1 || changedFilename) {
      $('#documents-upload').addClass('shown');
    } else {
      $('#document-upload-submit').trigger('click')
    }
  });
};
