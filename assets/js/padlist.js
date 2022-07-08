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

	request.addEventListener('loadend', function(event) {
		if(event.target.status == 200) {
			const padlist = JSON.parse(event.target.response);

			padlist.forEach(p => {
				const tr = document.querySelector('#pad-' + CSS.escape(p.id));

				// update public
				const aPublic = tr.querySelector('a');
				const spanIconPublic = tr.querySelector('td:nth-child(1) span.icon');
				const public = p.public === "True";
				aPublic.title = "Make this pad " + (public ? "private" : "public");
				spanIconPublic.innerHTML = "<i class=\"fas fa-" + (public ? "globe-americas" : "home") + "\"></i>";
				aPublic.onclick = () => padVisibility(p.id, public ? "private" : "public");

				// update lastEdit
				const tdLastEdit = tr.querySelector('td:nth-child(3)');
				const spanLastEdit = tdLastEdit.querySelector('span.tag');
				const spanIconLastEdit = tdLastEdit.querySelector('span.icon');
				delete tdLastEdit.dataset.sort;
				spanLastEdit.innerHTML = p.date;
				if(spanIconLastEdit !== null)
					spanIconLastEdit.remove();
			});

			sortPadList();
		} else {
			// update public
			document.querySelectorAll('#padTable td:nth-child(1) .fa-spinner').forEach(s => {
				const spanIcon = s.parentNode;
				const aPublic = spanIcon.parentNode;
				aPublic.title = "Error while loading";
				spanIcon.style.color = "red";
				spanIcon.innerHTML = "<i class=\"fas fa-times-circle\">";
			});
			// update lastEdit
			document.querySelectorAll('#padTable td:nth-child(3) .fa-spinner').forEach(s => {
				const spanIcon = s.parentNode;
				spanIcon.title = "Error while loading";
				spanIcon.style.color = "red";
				spanIcon.innerHTML = "<i class=\"fas fa-times-circle\">";
			});
		}
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
