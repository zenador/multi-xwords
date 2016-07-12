<?php require '../systemsubmitscore.php'; ?>
<?php

	/*

		CWORD JavaScript Crossword Engine

		Copyright (C) 2007-2010 Pavel Simakov
		http://www.softwaresecretweapons.com/jspwiki/cword

		This library is free software; you can redistribute it and/or
		modify it under the terms of the GNU Lesser General Public
		License as published by the Free Software Foundation; either
		version 2.1 of the License, or (at your option) any later version.

		This library is distributed in the hope that it will be useful,
		but WITHOUT ANY WARRANTY; without even the implied warranty of
		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
		Lesser General Public License for more details.

		You should have received a copy of the GNU Lesser General Public
		License along with this library; if not, write to the Free Software
		Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

	*/


	function hmac ($key, $data)
	{
	   // RFC 2104 HMAC implementation for php.
	   // Creates an md5 HMAC.
	   // Eliminates the need to install mhash to compute a HMAC
	   // Hacked by Lance Rushing

	   $b = 64; // byte length for md5
	   if (strlen($key) > $b) {
		   $key = pack("H*",md5($key));
	   }
	   $key  = str_pad($key, $b, chr(0x00));
	   $ipad = str_pad('', $b, chr(0x36));
	   $opad = str_pad('', $b, chr(0x5c));
	   $k_ipad = $key ^ $ipad ;
	   $k_opad = $key ^ $opad;

	   return md5($k_opad  . pack("H*",md5($k_ipad . $data)));
	}

	$hasError = false;
	$msg = "OK";

	$uid = $_REQUEST['uid'];	
	$data = $_REQUEST['data'];	
	$sign = $_REQUEST['sign'];	
	$seq = $_REQUEST['seq'];	
	$cookie = $_REQUEST['cookie'];	

	$check = hmac($uid, $data);
	if ($check != $sign){
		$hasError = true;
		$msg = "FAILED";
	}

	//$rank = "not yet known";
	$rank = -1;
   
	echo "oygSubmitScoreJSONComplete({  \"envelope\":  {\"success\":".(($hasError) ? "false" : "true").", \"seq\":".$seq.", \"cookie\":".$cookie.", \"msg\":\"".$msg."\"}, \"data\": {\"rank\": \"".$rank."\"}});";

	$dataray = array();
	$data = preg_replace('/^data:/', '', $data);
	$data = explode('&', $data);
	foreach ($data as &$datum) {
		list($part1, $part2) = explode('=', $datum);
		$dataray[$part1] = $part2;
	}
	unset($datum);

	/*$fh = fopen('./mystuff.txt', 'a') or die("can't open file");
	fwrite($fh, 'I am some text' . PHP_EOL);
	fclose($fh);*/
	file_put_contents('./userstats/'.$_SESSION['user']['username'].'.txt', 'ns:' . $dataray['ns']. PHP_EOL. 'finalscore:' . $dataray['finalscore']. PHP_EOL. 'score:' . $dataray['score']. PHP_EOL. 'deducts:' . $dataray['deducts']. PHP_EOL. 'checks:' . $dataray['checks']. PHP_EOL. 'reveals:' . $dataray['reveals']. PHP_EOL. 'revealletters:' . $dataray['revealletters']. PHP_EOL. 'hints:' . $dataray['hints']. PHP_EOL. 'time:' . $dataray['time']. PHP_EOL. PHP_EOL, FILE_APPEND);

?>