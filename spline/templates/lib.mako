<%def name="cache_content()"><%
    # This is set in spline.lib.base
    c._cache_me(context, caller)
%></%def>

<%def name="field(name, form=None, **render_args)">
<% form = form or c.form %>\
    <dt>${form[name].label() | n}</dt>
    <dd>${form[name](id=u'', **render_args) | n}</dd>
    % for error in form[name].errors:
    <dd class="error">${error}</dd>
    % endfor
</%def>

<%def name="bare_field(name, form=None, **render_args)">
<% form = form or c.form %>\
    ${form[name](id=u'', **render_args) | n}
    % for error in form[name].errors:
    <p class="error">${error}</p>
    % endfor
</%def>

<%def name="escape_html()" filter="h">${caller.body()}</%def>

<%def name="pager(skip, per_page, total, url_stuff)">
<%
    # All these page numbers are 1-based, like the display!
    import math
    page_ctx = 4
    cur_page = 1.0 * skip / per_page + 1
    prev_page = int(math.floor(cur_page - 0.001))
    next_page = int(cur_page + 1)
    num_pages = int(1.0 * (total - 1) / per_page) + 1

    if num_pages == 1 and cur_page == 1:
        # Nothing to show
        return

    # Build list of pages to go in the pager
    pages = []
    # Max space between the end and middle...
    # 1 2 ... 4 5 6 7 [8] => page_ctx + 3
    delta = page_ctx + 3
    # Before
    if prev_page - 1 < delta:
        pages.extend(range(1, prev_page + 1))
    else:
        pages.extend([1, 2, None])
        pages.extend(range(prev_page - page_ctx + 1, prev_page + 1))
    # Now
    pages.append(cur_page)
    # After
    if num_pages - next_page < delta:
        pages.extend(range(next_page, num_pages + 1))
    else:
        pages.extend(range(next_page, next_page + page_ctx - 1 + 1))
        pages.extend([None, num_pages - 1, num_pages])

    # Show the current page as an integer..  if possible
    if skip % per_page == 0:
        cur_page_pretty = int(cur_page)
    else:
        cur_page_pretty = "{0:.2f}".format(cur_page)

%>\
<ol class="pager">
    % for page in pages:
    % if page is None:
    <li class="dotdotdot">…</li>
    % elif page == cur_page:
    <li class="youarehere">${cur_page_pretty}</li>
    % else:
    <li>
        % if page == 1:
        <a href="${url(**url_stuff)}">
        % else:
        <a href="${url(skip=(page - 1) * per_page, **url_stuff)}">
        % endif

        % if page == 1:
        «
        % elif page == prev_page:
        ‹
        % endif
        ${page}
        % if page == num_pages:
        »
        % elif page == next_page:
        ›
        % endif

        </a>
    </li>
    % endif
    % endfor
</ol>
</%def>
