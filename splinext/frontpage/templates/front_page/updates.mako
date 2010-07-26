% for update in c.updates:
<%include file="${update.source.template}" args="update=update" />
% endfor
% if not c.updates:
<p>No updates.</p>
% endif

<p>Sources:</p>
<ul class="classic-list">
    % for source in c.sources:
    <li><a href="${source.link}"><img src="${h.static_uri('spline', "icons/{0}.png".format(source.icon))}" alt=""> ${source.title}</a></li>
    % endfor
</ul>
