// Modal
document.getElementById('newPad').addEventListener('click', () => {
	var createModal = document.getElementById('createModal');
	createModal.classList.toggle('is-active');
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
document.getElementById('modalButton').addEventListener('click', () => {
	var modalInput = document.getElementById('modalTextfield');
	var modalButton = document.getElementById('modalButton');

	// Check if there is a name for the new pad
	if(modalInput.value === "") {
		modalInput.classList.add('is-danger');
	} else {
		modalButton.classList.add('is-loading');

		var currGroup = document.getElementById('currentGroup').value;
		var newPadName = document.getElementById('modalTextfield').value;

		// Mach mal response
		// fail -> add class X
		// success -> add haken und lade seite neu
		request = new XMLHttpRequest();
		request.open("GET", '/uapi/CreatePad/' + currGroup + '/' + newPadName); // FIXME
		
		request.addEventListener('load', function(event) {
			console.log("Antwort");
			location.reload(); 
		});
		request.send();
	}
});



// Navbar
document.addEventListener('DOMContentLoaded', () => {

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
