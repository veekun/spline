<%namespace name="userlib" file="/users/lib.mako" />
% if c.user:
${h.form(url(controller='accounts', action='logout'), id='user')}
    Logged in as <a href="${url(controller='users', action='profile', id=c.user.id, name=c.user.name)}">${c.user.name}</a> ${userlib.color_bar(c.user)}.
    <input type="submit" value="Log out">
${h.end_form()}
% else:
<p id="user"><a href="${url(controller='accounts', action='login')}">Log in or register</a></p>
% endif
