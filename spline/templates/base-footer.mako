<%! from spline import i18n %>

<div id="footer-timer">
    ${_('Rendered in %s seconds') % h.timedelta_seconds(c.timer.total_time)} <br>
    ${_(
            '{queries} SQL {q} in {time:.02f} seconds',
            '{queries} SQL {q} in {time:.02f} seconds',
            n=c.timer.sql_queries
        ).format(
            queries=c.timer.sql_queries,
            time=h.timedelta_seconds(c.timer.sql_time),
            q=_('query', 'queries', n=c.timer.sql_queries),
        )}
</div>

<p> ${_('Powered by Spline')} </p>
<p> ${h.literal(_('Fugue icon set by <a href="http://www.pinvoke.com/">Yusuke Kamiyamane</a>; country flags by <a href="http://www.famfamfam.com/lab/icons/flags/">famfamfam</a>'))} </p>
