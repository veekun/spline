<%inherit file="/base.mako" />
<%namespace name="lib" file="/lib.mako" />
<%namespace name="userlib" file="/users/lib.mako" />

<%def name="title()">${c.page_user.name} - Users</%def>
<%def name="title_in_page()">User: ${c.page_user.name}</%def>

<h1>Edit ${c.page_user.name}'s profile</h1>

${h.secure_form(url.current(controller='users', action='profile_edit_commit'))}
<dl>
    <dt>Color ID</dt>
    <dd>${userlib.color_bar(c.page_user)}</dd>
    ${lib.field('name')}

    <dd><button type="submit">Save</button></dd>
</dl>
${h.end_form()}
