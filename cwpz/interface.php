<?php require 'system.php'; ?>
<html>
<head>
<script type="text/javascript">if (parent.frames.length > 0) top.location.href="interface.php";</script>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
<title>Crossword</title>
</head>
<frameset cols="75%,25%">
	<frame name="prog" src="blank.php">
	<frameset rows="50%,25%,25%">
		<frame name="options" src="options.php">
		<frame name="wordnet" src="../cgi-bin/cwpz/browsewordnet.cgi">
		<frame name="notes" src="blank.php">
	</frameset>
</frameset>
</html>