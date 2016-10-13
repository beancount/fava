const filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}$/;

function uploadDocument(formData) {
  const documentFolderIndex = $('#document-upload-folder').val();
  const filename = $('#document-name').val();

  formData.append('filename', filename);
  formData.append('targetFolderIndex', documentFolderIndex);

  $.ajax({
    type: 'PUT',
    url: $('#document-upload-submit').data('url'),
    data: formData,
    contentType: false,
    processData: false,
    success(data) {
      alert(data);
    },
    error(data) {
      alert(`Error while uploading:\n\n${data.responseText}`);
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

    const folders = $('#document-upload-folder option');
    if (!folders.length) {
      alert('You need to set the "documents" Beancount option to enable file uploads.');
      return;
    }

    const files = event.originalEvent.dataTransfer.files;
    const now = new Date();

    for (let i = 0; i < files.length; i += 1) {
      const formData = new FormData();
      const file = files[i];
      formData.append('file', file);
      formData.append('account_name', $(event.currentTarget).data('account-name'));

      let filename = file.name;

      if (filename.length < 11 || filenameRegex.test(filename.substring(0, 10)) === false) {
        filename = `${now.toISOString().substring(0, 10)} ${filename}`;
      }

      $('#document-name').val(filename);

      $('#document-upload-submit').click((e) => {
        e.preventDefault();
        uploadDocument(formData);
        $('#documents-upload').removeClass('shown');
      });

      if (folders.length > 1 || filename !== file.name) {
        $('#documents-upload').addClass('shown');
      } else {
        uploadDocument(formData);
      }
    }
  });
};
