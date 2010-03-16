<%inherit file="/base.mako" />
<%def name="title()">${c.message}</%def>

<h1>Error ${c.code}</h1>
<p>${c.message}</p>
