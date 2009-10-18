<!DOCTYPE html>
<html>
<head>
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" href="${url(controller='main', action='css')}">
    % for plugin, script in c.javascripts:
    <script type="text/javascript" src="${h.static_uri(plugin, 'script/%s.js' % script)}"></script>
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

<%def name="recursive_menu(links)">
<ul>
  % for label, url, childrens in links:
    <li>
        % if url:
        <a href="${url}">${label}</a>
        % else:
        <a>${label}</a>
        % endif
        % if childrens:
        ${recursive_menu(childrens)}
        % endif
    </li>
  % endfor
</ul>
</%def>
<div id="menu">
    ${recursive_menu(c.links)}
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
</div>
<div id="footer">
    <p> Powered by Spline </p>
    <p> Fugue icon set by <a href="http://www.pinvoke.com/">Yusuke Kamiyamane</a> </p>
</div>
</body>
</html>

<%def name="title()">Untitled</%def>
