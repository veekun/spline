<!DOCTYPE html>
<html>
<head>
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" href="${h.url_for(controller='main', action='css')}">
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
  % for link_tuple in links:
    % if len(link_tuple) > 2:
    ## Third one is childrens
    <li>
        <a href="${url(**link_tuple[1])}">${link_tuple[0]}</a>
        ${recursive_menu(link_tuple[2])}
    </li>
    % else:
    <li><a href="${url(**link_tuple[1])}">${link_tuple[0]}</a></li>
    % endif
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
