const filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}\.$/;

module.exports.initDocumentsUpload = function initDocumentsUpload() {
  function uploadDocuments(formData, filename, targetFolderIndex) {
    formData.append('filename', filename);
    formData.append('targetFolderIndex', targetFolderIndex);

    $.ajax({
      type: 'POST',
      url: window.documentsUploadUrl,
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
  if (window.documentsFolders.length > 0) {
    $('.droptarget').bind({
      dragenter(e) {
        e.stopPropagation();
        e.preventDefault();
      },
      dragover(e) {
        e.stopPropagation();
        e.preventDefault();
      },
      drop(e) {
        e.preventDefault();
        const files = e.originalEvent.dataTransfer.files;
        const today = new Date();

        for (let i = 0; i < files.length; i++) {
          const formData = new FormData();
          formData.append('file', files[i]);
          formData.append('account_name', $(this).attr('data-account-name'));

          let filename = files[i].name;

          if (filename.length < 11 || filenameRegex.test(filename.substring(0, 11)) === false) {
            filename = `${today.toISOString().substring(0, 10)}.${filename}`;
          }

          $('#documents-upload input#document-name').val(filename);
          $('#documents-upload input[type="submit"]').click((event) => {
            event.preventDefault();
            const documentFolderIndex = $('#documents-upload select#document-upload-folder').val();
            uploadDocuments(formData, filename, documentFolderIndex);
            $('.overlay-wrapper').hide();
          });

          if (window.documentsFolders.length <= 1) {
            $('#documents-upload select#document-upload-folder').hide();
            $('#documents-upload label#label-documents-upload-folder').hide();
          }

          if (filename === files[i].name) {
            $('#documents-upload input#document-name').hide();
            $('#documents-upload label#label-document-name').hide();
          }

          if (window.documentsFolders.length > 1 || filename !== files[i].name) {
            $('#documents-upload').show();
          } else {
            uploadDocuments(formData, filename, 0);
          }
        }
      },
    });
  }

  $('.droptarget').dragster({
    enter() {
      $(this).addClass('dragover');
    },
    leave() {
      $(this).removeClass('dragover');
    },
    drop() {
      $(this).removeClass('dragover');
    },
  });
};
