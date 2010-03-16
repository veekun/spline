<!DOCTYPE html>
<html>
<head>
    <title>${self.title()} - ${config['site_title']}</title>
    <link rel="shortcut icon" type="image/png" href="${h.static_uri('local', 'favicon.png')}">
    <link rel="stylesheet" type="text/css" href="${url(controller='main', action='css')}">
    % for plugin, script in c.javascripts:
    <script type="text/javascript" src="${h.static_uri(plugin, 'script/%s.js' % script)}"></script>
    % endfor
</head>
<body>
<div id="header">
    <div id="title">${config['site_title']}</div>
    <div id="page-name">${self.title_in_page()}</div>
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
  % for link in links:
    <li>
        % if link.url:
        <a href="${link.url}">${link.label}</a>
        % else:
        <a>${link.label}</a>
        % endif
        % if link.children:
        ${recursive_menu(link.children)}
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
    ## Allow easily overriding the timer; veekun wants to make it pretty
    <%include file="/base-timer.mako" />
    <p> Powered by Spline </p>
    <p> Fugue icon set by <a href="http://www.pinvoke.com/">Yusuke Kamiyamane</a>; country flags by <a href="http://www.famfamfam.com/lab/icons/flags/">famfamfam</a> </p>
</div>
</body>
</html>

<%def name="title()">Untitled</%def>
<%def name="title_in_page()">${self.title()}</%def>
