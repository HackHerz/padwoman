var sortPadList;

// based on https://stackoverflow.com/a/49041392
function initSortPadList() {
	const getCellValue = (tr, idx) => tr.children[idx].dataset.sort || tr.children[idx].innerText || tr.children[idx].textContent;

	const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
		v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
		)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

	const ths = document.querySelectorAll('#padTable th');

	const sort = th => {
		const tbody = document.querySelector('#padTable>tbody');
		Array.from(tbody.children)
			.sort(comparer(Array.from(th.parentNode.children).indexOf(th), th.classList.contains("asc")))
			.forEach(tr => tbody.appendChild(tr));

	};

	ths.forEach(th => {
		th.addEventListener('click', (() => {
			// flip arrow and remove from other ths
			const desc = th.classList.contains("desc");
			ths.forEach(th => {
				th.classList.remove("asc", "desc");
			});
			th.classList.add(desc ? "asc" : "desc");

			sortPadList = () => sort(th);
			sortPadList();
		}));
	});

	// initial sorting
	sortPadList = () => sort(document.querySelectorAll('#padTable th.asc, #padTable th.desc')[0]);
}

function reloadPadlist() {
	const currGroup = document.querySelector('#currentGroup').value;

	request = new XMLHttpRequest();
	request.open("GET", '/uapi/getPadlist/' + currGroup);

	request.addEventListener('load', function(event) {
		location.reload();
	});

	request.send();
}

document.addEventListener('DOMContentLoaded', () => {
	initSortPadList();
	sortPadList();

	// check if any data is not loaded
	if(document.querySelectorAll('#padTable td .fa-spinner').length > 0)
		reloadPadlist();
});
