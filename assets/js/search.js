var template = document.getElementById('result-template').innerHTML;

function renderResults(content) {
	var anchor = document.createElement('span');

	content.forEach(function(hit) {
		var el = document.createElement('span');
		el.innerHTML = template;

		// Title
		el.getElementsByClassName("search-title")[0].appendChild(
			document.createTextNode(hit.title));

		// Content
		if(hit.content) el.getElementsByClassName("search-content")[0].innerHTML = hit.content;

		// lastmod
		el.getElementsByClassName("search-lastmod")[0].appendChild(
			document.createTextNode(hit.lastmod));

		// URL
		el.getElementsByClassName("button")[0].href = hit.url;

		anchor.appendChild(el);
	});

	document.getElementById('searchresult').replaceChildren(anchor);
}


function search() {
	// Mach mal response
	request = new XMLHttpRequest();

	request.onreadystatechange = function() {
		if(this.readyState == 4 && this.status == 200) {
			response = JSON.parse(request.responseText);
			renderResults(response);
		}
	};

	request.open("GET", '/uapi/search', true);
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
