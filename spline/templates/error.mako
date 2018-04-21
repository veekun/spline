<%inherit file="/base.mako" />
<%! from spline import i18n %>
<%def name="title()">${c.message}</%def>

<h1>${_('Error %s') % c.code}</h1>
<p>${c.message}</p>
