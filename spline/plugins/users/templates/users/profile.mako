<%inherit file="/base.mako" />
<%namespace name="userlib" file="/users/lib.mako" />

<%def name="title()">${c.page_user.name} - Users</%def>

<h1>${c.page_user.name}'s profile</h1>

<p>
    Profile for ${c.page_user.name} ${userlib.color_bar(c.page_user)}.
    % if c.page_user == c.user:
    <a href="${url(controller='users', action='profile_edit', id=c.page_user.id, name=c.page_user.name)}">
        <img src="${h.static_uri('spline', 'icons/user--pencil.png')}" alt="">
        Edit
    </a>
    % endif
</p>
