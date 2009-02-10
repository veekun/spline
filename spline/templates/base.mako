<html>
<head>
    <title>${self.title()}</title>
</head>
<body>
    % if 'users' in config['spline.plugins']:
    % if c.user:
    <p> Welcome, ${c.user.name}! </p>
    % else:
    <p> <!-- login form --> </p>
    % endif
    % endif

    ${next.body()}
</body>
</html>

<%def name="title()">Untitled</%def>
