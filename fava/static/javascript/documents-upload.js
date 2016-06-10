module.exports.initDocumentsUpload = function() {
  function uploadDocuments(formData, filename, targetFolderIndex) {
    formData.append('filename', filename);
    formData.append('targetFolderIndex', targetFolderIndex);

    $.ajax({
      type: 'POST',
      url: window.documentsUploadUrl,
      data: formData,
      contentType: false,
      cache: false,
      processData: false,
      async: false,
      success: function(data) {
        alert(data);
      },
      error: function(data) {
        alert("Error while uploading:\n\n" + data.responseText);
      }
    });
  }

  // File uploads via Drag and Drop on elements with class "droptarget" and
  // attribute "data-account-name"
  if (window.documentsFolders.length > 0) {
    $('.droptarget').bind({
      dragenter: function(e) {
        e.stopPropagation();
        e.preventDefault();
      },

      dragover: function(e) {
        e.stopPropagation();
        e.preventDefault();
      },

      drop: function(e) {
        e.preventDefault();
        var files = e.originalEvent.dataTransfer.files;

        for (var i = 0; i < files.length; i++) {
          var formData = new FormData();
          console.log(files[i]);
          formData.append('file', files[i]);
          formData.append('account_name', $(this).attr('data-account-name'));

          var filename = files[i].name;
          var filenameRegex = /^\d{4}-\d{1,2}-\d{1,2}\.$/;

          if (filename.length < 11 || filenameRegex.test(filename.substring(0, 11)) === false) {
            var today = new Date();
            filename = today.toISOString().substring(0, 10) + '.' + filename;
          }

          $('#documents-upload input#document-name').val(filename);
          $('#documents-upload input[type="submit"]').click(function(event) {
            event.preventDefault();
            var documentFolderIndex = $('#documents-upload select#document-upload-folder').val();
            uploadDocuments(formData, filename, documentFolderIndex);
            $('.overlay-wrapper').hide();
          });

          if (window.documentsFolders.length <= 1) {
            $('#documents-upload select#document-upload-folder').hide();
            $('#documents-upload label#label-documents-upload-folder').hide();
          }

          if (filename == files[i].name) {
            $('#documents-upload input#document-name').hide();
            $('#documents-upload label#label-document-name').hide();
          }

          if (window.documentsFolders.length > 1 ||  filename != files[i].name) {
            $('#documents-upload').show();
          } else {
            uploadDocuments(formData, filename, 0)
          }
        }
      }
    });
  }

  $('.droptarget').dragster({
    enter: function(dragsterEvent, event) {
      $(this).addClass('dragover');
    },
    leave: function(dragsterEvent, event) {
      $(this).removeClass('dragover');
    },
    drop: function(dragsterEvent, event) {
      $(this).removeClass('dragover');
    }
  });
}
