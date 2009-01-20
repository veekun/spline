<%inherit file="base.mako" />

% if 'users' in config['spline.plugins']:
% if 'user_id' in session:
<p> Welcome, user #${session['user_id']}! </p>
% else:
<p> <!-- login form --> </p>
% endif
% endif
