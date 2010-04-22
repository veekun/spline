% if c.user:
${h.form(url(controller='accounts', action='logout'), id='user')}
    Logged in as ${c.user.name}.
    <input type="submit" value="Log out">
${h.end_form()}
% else:
${h.form(url(controller='accounts', action='login_begin'), id='user')}
    <img src="${h.static_uri('spline', 'icons/openid.png')}">
    <input type="text" name="openid" size="30">
    <input type="submit" value="Log in">
${h.end_form()}
% endif
