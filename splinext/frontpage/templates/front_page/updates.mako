% if c.updates and not c.last_seen_item:
    <hr class="frontpage-new-stuff">
% endif
% for update in c.updates:
    <%include file="${update.source.template}" args="update=update" />
    % if update == c.last_seen_item:
    <hr class="frontpage-new-stuff">
    % endif
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
