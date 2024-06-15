(function($) {
  'use strict';
  if ($("#fileuploader").length) {
    $("#fileuploader").uploadFile({
      url: "../../../{%static 'glam_admin/images/",
      fileName: "myfile"
    });
  }
})(jQuery);