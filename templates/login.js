<script>

	document.getElementById('loginForm').onsubmit = function() {
		var formPassword = document.getElementById('password');
		var formUser = document.getElementById('username');

		formPassword.classList.remove('is-danger');
		formUser.classList.remove('is-danger');


		// Username is empty
		if(formUser.value === "") {
			formUser.classList.add('is-danger');
			return false;
		}
		
		// Password is empty
		if(formPassword.value === "") {
			formPassword.classList.add('is-danger');
			return false;
		}

		return true;
	};

</script>
