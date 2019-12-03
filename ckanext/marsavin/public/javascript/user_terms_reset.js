// Add ckan module
this.ckan.module('user-terms-reset', function(jQuery, _) {
  return {
    options: {
    },
    initialize: function() {
      jQuery('#field-user-terms-agree').change(function() {
          if(this.checked) {
              jQuery(".form-actions").find("button.btn-primary").attr("disabled", false);
          } else {
              jQuery(".form-actions").find("button.btn-primary").attr("disabled", true);
          }
      });
      jQuery(".form-actions").find("button.btn-primary").attr("disabled", true);
      jQuery("#tooltip-user-terms-agree").tooltip();
    }
  }
});