<!DOCTYPE html>
<html>
<head>
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" href="${h.url_for(controller='main', action='css')}">
## XXX Should this be done for CSS, too?
    % for script in c.javascripts:
    <script type="text/javascript" src="/script/${script}.js"></script>
    % endfor
</head>
<body>
<div id="header">
    <div id="title">Veekun</div>
    <div id="page-name">Index</div>
    % if 'users' in config['spline.plugins']:
    <div id="user">
    % if c.user:
    <p> Welcome, ${c.user.name}! </p>
    % else:
    <p> <!-- login form --> </p>
    % endif
    </div>
    % endif
    <%include file="/widgets.mako" args="widget='page_header'"/>
</div>
## I hate wrapper divs, but these allow for some very nice layout.
## #content is used for columns; +padding, -margin, overflow: hidden.
## #body-wrapper is used for any-source-order columns.
<div id="body">
 <div id="content-wrapper">
  <div id="content">
    ${next.body()}
  </div>
 </div>
 <div id="menu">
    <ul>
    <li><a href="${h.url_for(controller='main', action='index')}">Home</a></li>
    </ul>

 </div>
</div>
<div id="footer">
    <p> Powered by Spline
</div>
</body>
</html>

<%def name="title()">Untitled</%def>
