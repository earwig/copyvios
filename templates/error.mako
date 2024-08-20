<%include file="/includes/header.mako" args="title='Error! - Earwig\'s Copyvio Detector'"/>
<h2>Error!</h2>
<p>An error occurred. If it hasn't been reported (<a href="https://github.com/earwig/copyvios/issues">try to check</a>), please <a href="https://github.com/earwig/copyvios/issues/new">file an issue</a> or <a href="mailto:wikipedia.earwig@gmail.com">email me</a>. Include the following information:</p>
<div id="info-box" class="red-box">
    <pre>${traceback | trim,h}</pre>
</div>
<%include file="/includes/footer.mako"/>
