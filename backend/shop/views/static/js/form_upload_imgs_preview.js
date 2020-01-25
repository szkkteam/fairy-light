/*
	Resources:
	- https://learn.jquery.com/plugins/basic-plugin-creation/
*/
(function ( $ ) {
	
	$.fn.imgUpload = function ( options ) {
		options = options || {};
		
		/* Configure options */
		var opts = $.extend( {}, $.fn.imgUpload.defaults, options );
		const getFileExtension = /(?:\.([^.]+))?$/;
				
		
		/* *********************************************
	       * Callback register Section
		   ********************************************* */		
		/* Register a callbacks on form submit and file select events. */
		var form = this;
		form.find('input[type=file]').on('change', handleFileSelect, false );
		form.on('submit', handleFormSubmit, false );
		
		
		/* *********************************************
		   * Image Preview Building Section
		   ********************************************* */		
		function preparePreviewElement ( ) {
			var separator = $(form).find("#image-preview-separator");
			/* If Separator alrady added, crlear it's inner HTML else add the spearator div */
			if (separator.length) {
				separator.html("");
			} else {
				separator = $("<div>", { "id": "image-preview-separator"});
				if (opts.imgPreviewElement == null) {
					$(form).append(separator);
				} else {
					$(opts.imgPreviewElement).append(separator);
				}			
			}
			return separator;						
		};
		
		function handleFileSelect ( e ) {
			if(!e.target.files || !window.FileReader) return;

			/* Prepare the file preview section by deleting all the previous previews. */
			var section = preparePreviewElement();

			var files = e.target.files;
			var filesArr = Array.prototype.slice.call(files);
			filesArr.forEach(function(f) {
				if(!f.type.match("image.*")) {
					return;
				}
				var reader = new FileReader();
				reader.onload = function (e) {
					section.append(buildPreviewHtml(e.target.result, f.name));
				}
				reader.readAsDataURL(f);
			});
		};
		
		function buildPreviewHtml(src, filename) {
			var progressbar_div = $("<div>", { "class": "progress", "hidden": "", "style": "margin-bottom:0px" }).append(
			  $("<div>", { "class": "progress-bar", "role": "progressbar", "aria-valuenow": "0", "aria-valuemin": "0", "aria-valuemax": "100", "style": "width:0%" })
			);
			var table = $("<tr>", { "class" : "image-name-container", "style": "position:relative"});

			table.append(
				$("<td>", { "style": "width:30%" }).append(
				"<img class=\"img-preview\" src=\"" + src + "\">"
			));

			var input = $("<input>", { "class": "img-name", "type": "text", "placeholder": filename });
			input.attr('size', input.attr('placeholder').length);

			table.append(
				$("<td>").append(
				input
			));

			table.append(
				$("<td>", {"style": "width:200px"}).append(
					progressbar_div
				));

			return table;
		}
		
		/* *********************************************
	       * Form Submit Section
		   ********************************************* */		
		function getAllFormInputs () {
			/* Get all input elements */
			if (opts.inputElements) {
				return opts.inputElements;
			} else {
				return $(form).find(':input');					
			}			
		};
		
		
		
		
		function handleFormSubmit( e ) {
			e.preventDefault();
		};
		
				
		return this;
	};	
	
	$.fn.imgUpload.defaults = {
		onSuccessImgUpload : function ( element ) {},
		onFailedImgUpload : function ( element ) {},
		onSuccessOperation : function () {},
		onFailedOperation : function () {},
		imgPreviewElement : null,
		inputElements : null,
		/* buildPreview = function (src, filename ) { return buildPreviewHtml(src, filename) },*/
		/*
		foreground: "red",
		background: "yellow"
		*/
	};
	
}( jQuery ));

