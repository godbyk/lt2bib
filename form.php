<?php require('logograms.php'); ?>

<h1>LibraryThing to <?php echo $logo_bibtex; ?></h1>

<div class="content">
<div class="content-columns">
<div class="content-column-left">
<h2>What is this?</h2>
<p>This page will generate a <?php echo $logo_bibtex; ?> file from your <a href="http://www.librarything.com/" title="LibraryThing">LibraryThing</a> data in three easy steps!</p>
<ol>
<li><a href="http://www.librarything.com/export-tab.php" title="Export my LibraryThing data">Download your LibraryThing data</a>.</li>
<li>Upload the <tt>LibraryThing_TD.xls</tt> file.</li>
<li>Click on the <b>Generate BibTeX</b> button below.</li>
</ol>

<h2>Upload your LibraryThing library</h2>

<form action="lt2bib.cgi" method="post" name="lt2bib" id="lt2bib" enctype="multipart/form-data">
<div class="bluebg">
<input name="MAX_FILE_SIZE" type="hidden" value="7340032" />
<label for="lt_file">Upload your <tt>LibraryThing_TD.xls</tt> file:<br/>
<input size="40" name="lt_file" type="file" />
</label>
<br />
<!-- TODO
<tr><td align="left">
	<label for="generate_latex_checkbox">
	<input name="generate_latex" type="checkbox" value="1" id="generate_latex_checkbox" />
	Generate <?php echo $logo_latex; ?> test file
	</label>
</td></tr>
-->
<br />
<div class="aligncenter"><input value="Generate BibTeX" type="submit" /></div>
</div>
</form>
		</div> <!-- /content-column-left -->

		<div class="content-column-right">
			<h2>Need help?</h2>
			<p>If you have any problems uploading your LibraryThing file, or if you have problems using the resulting <?php echo $logo_bibtex; ?> file, please <a href="mailto:godbyk@gmail.com?subject=lt2bib problems" title="Email Kevin">email me</a>.  Please attach a copy of your <tt>LibraryThing_TD.xls</tt> file to your email so I can use it when troubleshooting your problem.</p>
			<p>Also, please <a href="mailto:godbyk@gmail.com?subject=lt2bib suggestions" title="Email Kevin">let me know</a> if you have any suggestions for improvements.</p>
			
			<h2>My To Do List</h2>
			<p>Here is a list of known bugs and feature requests that I'm working on:</p>
			<ul>
			<li>Find a better way to deal with missing data (e.g., if the author and editor are both missing).</li>
			<li>Parse editors, volumes, and editions.</li>
			</ul>
		</div> <!-- /content-column-right -->
	</div> <!-- /content-columns -->

	<hr />
	<div class="content-middle">
	</div> <!-- /content-middle -->
</div> <!-- /content -->

