<?php
	$username = $_POST['username'];
	$password = $_POST['password'];

	if (!empty($username) || !empty($password)) {
		$host = 'localhost';
		$user = 'root';
		$dbpassword = 'yuvrajroot';
		$dbname = 'covid19';

		// create connection
		$conn new mysqli($host, $user, $dbpassword, $dbname)
		if (mysql_connect_error()) {
			die('Connect Error('.mysqli_connect_errno().')'.mysqli_connect.error());
		}
		else{
			$SELECT = 'SELECT username FROM user WHERE username=? limit 1';
			$INSERT = 'INSERT INTO user (username, password) VALUES (?, ?)';

			//prepare statement 
			$stmt = $conn -> prepare($SELECT);
			$stmt -> mysqli_bind_param("s", $username);
			$stmt -> execute();
			$stmt -> mysqli_bind_result($username);
			$stmt -> store_result();
			$rownum = $stmt->num_rows

			if ($rownum==0) {
				$stmt-> close();

				$stmt = $conn->prepare($INSERT);
				$stmt-> mysqli_bind_param("ss", $username, $password);

				$stmt -> execute();
				echo "Inserted Successfully";
			}
			else {
				echo "Email ALready Registered";
			}
			$stmt -> close();
			$conn -> close();

		}
	}
	else {
		echo "all fields are required";
		die();
	}
?>