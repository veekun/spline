${h.form(url(controller='accounts', action='login_begin'), id='user')}
    % if c.user:
    Logged in as ${c.user.name}.
    % else:
    <img src="${h.static_uri('spline', 'icons/openid.png')}">
    <input type="text" name="openid" size="30">
    <input type="submit" value="Log in">
    % endif
${h.end_form()}
