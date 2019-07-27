var modalPadname = document.getElementById('modalPadname');
var modalDate = document.getElementById('modalDate');
var modalTime = document.getElementById('modalTime');
var modalNow = document.getElementById('modalNow');
var modalReset = document.getElementById('modalReset');
var modalPadnamePreview = document.getElementById('modalPadnamePreview');
var createModal = document.getElementById('createModal');



function updatePadnamePreview() {
	var padname = modalPadname.value;

	if (modalDate != null)
		padname = padname.replace(/{{ *date *}}/g, modalDate.value);

	if (modalTime != null)
		padname = padname.replace(/{{ *time *}}/g, modalTime.value);

	if (modalTime != null && modalDate != null)
		padname = padname.replace(/{{ *datetime *}}/g, modalDate.value + '_' + modalTime.value);

	modalPadnamePreview.value = padname;
}



function resetDatetime(now = false) {
	const nowDate = new Date();

	if (modalDate != null)
		if (now || modalDate.defaultValue === "")
			modalDate.value = nowDate.getFullYear() + '-' + ('0' + (nowDate.getMonth() + 1)).substr(-2) + '-' + ('0' + nowDate.getDate()).substr(-2);
		else
			modalDate.value = modalDate.defaultValue;

	if (modalTime != null)
		if (now || modalTime.defaultValue === "")
			modalTime.value = ('0' + nowDate.getHours()).substr(-2) + ':' + ('0' + nowDate.getMinutes()).substr(-2);
		else
			modalTime.value = modalTime.defaultValue;

	updatePadnamePreview();
}



// Modal
document.getElementById('newPad').addEventListener('click', () => {
	createModal.classList.toggle('is-active');

	resetDatetime();

	if(createModal.classList.contains('is-active')) {
		modalPadname.focus();
	}
});



if(modalPadnamePreview != null) {
	modalPadname.addEventListener('input', updatePadnamePreview);
	if (modalDate != null)
		modalDate.addEventListener('input', updatePadnamePreview);
	if (modalTime != null)
		modalTime.addEventListener('input', updatePadnamePreview);
	if (modalNow != null)
		modalNow.addEventListener('click', e => resetDatetime(true));
	if (modalReset != null)
		modalReset.addEventListener('click', e => resetDatetime());
}



// Closing the modal
document.getElementById('createModalClose').addEventListener('click', () => {
	createModal.classList.toggle('is-active');

	// remove warning and input from textfield
	modalPadname.classList.remove('is-danger');
	document.getElementById('modalForm').reset();
});



// Creating a new Pad
function submitFunction(e) {
	var modalButton = document.getElementById('modalButton');
	var modalError = document.getElementById('modalError');

	modalError.innerHTML = "";
	var fillPadWithContent = false;

	// check if there are radiobuttons
	// check if they are true
	rButton = document.getElementById('newPadSetContent');

	if(rButton != null) {
		fillPadWithContent = rButton.checked;
	}


	// Check if there is a name for the new pad
	if(modalPadname.value.trim() === "") {
		modalPadname.classList.add('is-danger');
	} else {
		modalButton.classList.add('is-loading');

		var currGroup = document.getElementById('currentGroup').value;
		var newPadName = modalPadname.value;

		var timestamp = ""
		if(modalDate != null && modalTime != null)
			timestamp = '/' + modalDate.value + 'T' + modalTime.value;
		else if(modalDate != null)
			timestamp = '/' + modalDate.value;
		else if(modalTime != null)
			timestamp = '/' + modalTime.value;


		// Mach mal response
		request = new XMLHttpRequest();
		
		request.onreadystatechange = function() {
			if(this.readyState == 4 && this.status == 200) {
				modalButton.classList.remove('is-loading');

				response = JSON.parse(request.responseText);

				// success
				if(response.code == 0) { // Success
					modalPadname.value = modalPadname.getAttribute('data-padname');
					modalError.classList.remove('is-danger');
					modalError.classList.add('is-success');
					modalError.innerHTML = "Success! Please wait...";
					location.reload(); 
				} else { // failure in pad creation
					modalError.innerHTML = response.message	
				}
			}
		};

		if(fillPadWithContent) { // set content
			request.open("GET", '/uapi/CreateContentPad/' + currGroup + '/' + newPadName + timestamp, true);
		} else { // dont set content
			request.open("GET", '/uapi/CreatePad/' + currGroup + '/' + newPadName + timestamp, true);
		}
		request.send();
	}

	return false;
}


/*
 * visibility toggle stuff
 */
function padVisibility(pad, newStatus) {

	request = new XMLHttpRequest();
	request.open("GET",
		'/uapi/PadVisibility/' + pad + '/' + newStatus);

	request.addEventListener('load', function(event) {
		location.reload(); 
	});

	request.send();
}



// Navbar
document.addEventListener('DOMContentLoaded', () => {
	/*
	 * Navbar Stuff
	 */
	// Get all "navbar-burger" elements
	const $navbarBurgers = Array.prototype.slice.call(
		document.querySelectorAll('.navbar-burger'), 0);

	// Check if there are any navbar burgers
	if ($navbarBurgers.length > 0) {

		// Add a click event on each of them
		$navbarBurgers.forEach( el => {
			el.addEventListener('click', () => {

				// Get the target from the "data-target" attribute
				const target = el.dataset.target;
				const $target = document.getElementById(target);

				// Toggle the "is-active" class on both the "navbar-burger" and
				// the "navbar-menu"
				el.classList.toggle('is-active');
				$target.classList.toggle('is-active');

			});
		});
	}


	/*
	 * Contextmenu Stuff
	 */
	tippy('a[name=contextMenu]', {
		content(reference) {
			const id = reference.getAttribute('data-padid');
			var template = document.getElementById("contextMenu-template");
			let button = template.querySelector('a');
			button.href = "/uapi/ExportLatex/" + id;
			return template.innerHTML;
		},
		allowHTML: true,
		interactive: true,
		trigger: 'click',
		hideOnClick: true,
	});
});
