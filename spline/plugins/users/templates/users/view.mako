<%inherit file="/base.mako" />
<%def name="title()">${c.page_user.name} - Users</%def>
<%def name="title_in_page()">User: ${c.page_user.name}</%def>

<h1>${c.page_user.name}</h1>

A user!
