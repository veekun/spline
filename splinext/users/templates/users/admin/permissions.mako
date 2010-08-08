<%inherit file="/base.mako" />

<%def name="title()">Permissions - User admin</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='users', action='list')}">Users</a></li>
    <li>Permissions admin</li>
</ul>
</%def>

<h1>Roles</h1>

<ul class="classic-list">
    % for role in c.roles:
    <li>
        <img src="${h.static_uri('spline', "icons/{0}.png".format(role.icon))}" alt="">
        ${role.name}

        <ul class="classic-list">
            % for role_permission in role.role_permissions:
            <li>${role_permission.permission}</li>
            % endfor
        </ul>
    </li>
    % endfor
</ul>
