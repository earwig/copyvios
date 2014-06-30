<%include file="/support/header.mako" args="title='Error! - Earwig\'s Copyvio Detector'"/>
<div id="info-box" class="red-box">
    <p>An error occured! If it hasn't been reported (<a href="https://github.com/earwig/copyvios/issues">try to check</a>), please <a href="https://github.com/earwig/copyvios/issues/new">file an issue</a> or <a href="mailto:wikipedia.earwig@gmail.com">email me</a>. Include the following information:</p>
    <pre>{{traceback | h}}</pre>
</div>
<%include file="/support/footer.mako"/>
