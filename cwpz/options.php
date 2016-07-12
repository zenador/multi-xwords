<?php require 'system.php'; ?>
<?php 
	if(!empty($_POST)) 
	{
		$query_params = array( 
			':gridlength' => $_POST['gridlength'], 
			':sollang' => $_POST['sollang'], 
			':cluelang' => $_POST['cluelang'], 
			':cluetype' => $_POST['cluetype'], 
			':clue2type' => $_POST['clue2type'], 
			':forceclue2' => $_POST['forceclue2'], 
			':user_id' => $_SESSION['user']['id'], 
			':playcount' => $_SESSION['user']['playcount'] + 1, 
		); 
		 
		$query = " 
			UPDATE users 
			SET 
				gridlength = :gridlength,
				sollang = :sollang,
				cluelang = :cluelang,
				cluetype = :cluetype,
				clue2type = :clue2type,
				forceclue2 = :forceclue2,
				playcount = :playcount
			WHERE 
				id = :user_id 
		"; 
		 
		try 
		{ 
			$stmt = $db->prepare($query); 
			$result = $stmt->execute($query_params); 
		} 
		catch(PDOException $ex) 
		{ 
			// Note: On a production website, you should not output $ex->getMessage(). 
			// It may provide an attacker with helpful information about your code.  
			die("Failed to run query: " . $ex->getMessage()); 
		} 
		 
		$_SESSION['user']['gridlength'] = $_POST['gridlength'];
		$_SESSION['user']['sollang'] = $_POST['sollang'];
		$_SESSION['user']['cluelang'] = $_POST['cluelang'];
		$_SESSION['user']['cluetype'] = $_POST['cluetype'];
		$_SESSION['user']['clue2type'] = $_POST['clue2type'];
		$_SESSION['user']['forceclue2'] = $_POST['forceclue2'];
		$_SESSION['user']['playcount'] += 1;
		 
		header("Location: options.php"); 
		die("Redirecting to options.php"); 
	} 
?>

<html>
<head>
<script type="text/javascript">if (parent.frames.length == 0) location.href="interface.php";</script>
<meta http-equiv='Content-Type' content='text/html; charset=utf-8'/>
<title>Crossword options</title>
<script type="text/javascript">
function subandref(){
	document.forms['options'].action='options.php';
	document.forms['options'].target='_self';
	//document.forms['options'].submit();

	document.forms['options'].action='../cgi-bin/cwpz/crossword.cgi';
	document.forms['options'].target='prog';
	document.forms['options'].submit();

	//setTimeout("window.parent.prog.location.reload();", 0);
	//return true;
}
function load(){
	document.forms['notebook'].action='../cgi-bin/cwpz/notebook.cgi';
	document.forms['notebook'].target='notes';
	document.forms['notebook'].submit();

	//setTimeout("window.parent.prog.location.reload();", 0);
	//return true;
}
</script>
<style type="text/css">
body { font-family:"Times New Roman", Times, serif; font-size: 16px; }
</style>
</head>
<body onload="load()">

<form action="../cgi-bin/cwpz/crossword.cgi" id="options" method="post" target="prog">
Grid Length = <input name="gridlength" type="text" size="2" maxlength="2" value="<?php echo $_SESSION['user']['gridlength']; ?>" /><br/>
<?php $langs = array('als' => 'Albanian', 'arb' => 'Arabic', 'ind' => 'Bahasa Indonesia', 'zsm' => 'Bahasa Melayu', 'eus' => 'Basque', 'nob' => 'Bokmål', 'por' => 'Brazilian Portuguese', 'cat' => 'Catalan', 'dan' => 'Danish', 'eng' => 'English', 'fin' => 'Finnish', 'fre' => 'French', 'glg' => 'Galician', 'heb' => 'Hebrew', 'ita' => 'Italian', 'jpn' => 'Japanese', 'cmn' => 'Mandarin Chinese - Taiwan', 'nno' => 'Nynorsk', 'fas' => 'Persian', 'pol' => 'Polish', 'spa' => 'Spanish', 'tha' => 'Thai'); ?>
Solution language:
<select name="sollang">
<?php
foreach ($langs as $key => &$value) {
	echo "<option value=\"$key\"";
	if($_SESSION['user']['sollang'] == $key) {
		echo ' selected="yes"';
	}
	echo ">$value</option>$key" . PHP_EOL;
}
?>
</select><br/>
Clue language:
<select name="cluelang">
<?php
foreach ($langs as $key => &$value) {
	echo "<option value=\"$key\"";
	if($_SESSION['user']['cluelang'] == $key) {
		echo ' selected="yes"';
	}
	echo ">$value</option>$key" . PHP_EOL;
}
?>
</select><br/>
Clue type:
<select name="cluetype">
<?php
$cluetypes = array('1' => 'Synonyms', '2' => 'Definition', '3' => 'Examples', '4' => 'Japanese Kanji', '5' => 'Images');
foreach ($cluetypes as $key => &$value) {
	echo "<option value=\"$key\"";
	if($_SESSION['user']['cluetype'] == $key) {
		echo ' selected="yes"';
	}
	echo ">$value</option>$key" . PHP_EOL;
}
?>
</select><br/>
Alternative clue type:
<select name="clue2type">
<?php
$cluetypes = array('1' => 'Synonyms', '2' => 'Definition', '3' => 'Examples', '4' => 'Japanese Kanji');
foreach ($cluetypes as $key => &$value) {
	echo "<option value=\"$key\"";
	if($_SESSION['user']['clue2type'] == $key) {
		echo ' selected="yes"';
	}
	echo ">$value</option>$key" . PHP_EOL;
}
?>
</select>
Force?
<?php
echo "<input type=\"checkbox\" name=\"forceclue2\" value=\"1\"";
if($_SESSION['user']['forceclue2'] == '1') {
	echo ' checked="checked"';
}
echo "/><br/>" . PHP_EOL;
?>
<input name="username" type="hidden" value="<?php echo $_SESSION['user']['username']; ?>" />
<input type="button" value="Generate Puzzle" onClick="subandref()" />
</form>
<form action="../cgi-bin/cwpz/notebook.cgi" id="notebook" method="post" target="notes">
<input name="username" type="hidden" value="<?php echo $_SESSION['user']['username']; ?>" />
</form>
<a href="edit_account.php">Edit Account</a><br/>
<a href="logout.php">Logout</a><br/><br/>

Disclaimer: The contents of the database are drawn from an external source (WordNet) and may not be completely accurate, so use this at your own risk. The word frequencies in particular are not very reliable, so you may find weird words and definitions in your puzzle.<br/><br/>

It is normal for the puzzle to take more than a minute to load at times, so please be patient.<br/><br/>

Please note that the current database only has definitions and examples for English, Japanese and Albanian. If you select definitions or examples for any other language, you will be given synonyms as hints instead. If you select Kanji as the clue, the solution language will be Japanese. Alternative clues may be viewed by clicking on the number of the corresponding clue in the list of clues. Ticking the 'Force?' checkbox means that there will be alternative clues for every item, but that may also narrow down the words that may possibly appear in the crossword.<br/><br/>

Using the custom word list below means that the crossword will not be generated from a random selection of words in the database. If you want a random puzzle, please replace all the text in the box below with a space and then click the save button.<br/><br/>

Example of how to format your custom word list (just start with the following and experiment, but make sure your solution language matches the words):<br/>
w dolphin<br/>
wc earth the planet on which we live<br/>
wc sun great ball of gas|in the sky during the day<br/>
s 03837422-n<br/>
sw 09270894-n earth<br/>
sw 09444100-n star<br/><br/>

Or you could copy-and-paste from these word lists:<br/>
<a href="lists/jlpt-n5.txt" target="_blank">JLPT N5</a><br/>
<a href="lists/jlpt-n4.txt" target="_blank">JLPT N4</a><br/>
<a href="lists/jlpt-n3.txt" target="_blank">JLPT N3</a><br/>
<a href="lists/jlpt-n2.txt" target="_blank">JLPT N2</a><br/>
<a href="lists/jlpt-n1.txt" target="_blank">JLPT N1</a><br/><br/>

<a href="https://github.com/zenador/multi-xword">Source code here</a>

</body>
</html>
