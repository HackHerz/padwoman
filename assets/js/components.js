// Modal
document.getElementById('newPad').addEventListener('click', () => {
	var createModal = document.getElementById('createModal');
	createModal.classList.toggle('is-active');

	if(createModal.classList.contains('is-active')) {
		document.getElementById('modalTextfield').focus();
	}
});



// Closing the modal
document.getElementById('createModalClose').addEventListener('click', () => {
	var createModal = document.getElementById('createModal');
	createModal.classList.toggle('is-active');

	// remove warning and input from textfield
	var modalInput = document.getElementById('modalTextfield');
	modalInput.classList.remove('is-danger');
	document.getElementById('modalForm').reset();
});



// Creating a new Pad
function submitFunction(e) {
	var modalInput = document.getElementById('modalTextfield');
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
	if(modalInput.value.trim() === "") {
		modalInput.classList.add('is-danger');
	} else {
		modalButton.classList.add('is-loading');

		var currGroup = document.getElementById('currentGroup').value;
		var newPadName = modalInput.value;

		// Mach mal response
		request = new XMLHttpRequest();
		
		request.onreadystatechange = function() {
			if(this.readyState == 4 && this.status == 200) {
				modalButton.classList.remove('is-loading');

				response = JSON.parse(request.responseText);

				// success
				if(response.code == 0) { // Success
					modalInput.value = modalInput.getAttribute('data-padname');
					location.reload(); 
				} else { // failure in pad creation
					modalError.innerHTML = response.message	
				}
			}
		};

		if(fillPadWithContent) { // set content
			request.open("GET", '/uapi/CreateContentPad/' + currGroup + '/' + newPadName, true);
		} else { // dont set content
			request.open("GET", '/uapi/CreatePad/' + currGroup + '/' + newPadName, true);
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
});
