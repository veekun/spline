<%inherit file="/base.mako" />
<%namespace name="userlib" file="/users/lib.mako" />

<%def name="title()">Users</%def>

<h1>Users</h1>

<ul class="classic-list">
    % for user in c.users:
    <li>
        <a href="${url(controller='users', action='profile', id=user.id, name=user.name)}">
            ${userlib.color_bar(user)} ${user.name}
        </a>
    </li>
    % endfor
</ul>
