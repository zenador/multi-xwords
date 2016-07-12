<?php require 'system.php'; ?>
<html>
<head>
<script type="text/javascript">if (parent.frames.length > 0) top.location.href="../cwpz/interface.php";</script>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
<title>Crossword</title>
</head>
<frameset cols="80%,20%">
	<frame name="prog" src="../cgi-bin/cwpz/crossword.cgi">
	<frameset rows="50%,50%">
		<frame name="options" src="../cgi-bin/cwpz/options.cgi">
		<frame name="wordnet" src="../cgi-bin/cwpz/browsewordnet.cgi">
	</frameset>
</frameset>
</html>