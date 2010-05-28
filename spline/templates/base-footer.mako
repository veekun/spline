<%def name="format_timedelta(delta)">${ "{0:.02f}".format( delta.seconds + delta.microseconds / 1000000.0 ) }</%def>

<div id="footer-timer">
    Rendered in ${format_timedelta(c.timer.total_time)} seconds <br>
    ${c.timer.sql_queries} SQL quer${ 'y' if c.timer.sql_queries == 1 else 'ies' }
        in ${format_timedelta(c.timer.sql_time)} seconds
</div>

<p> Powered by Spline </p>
<p> Fugue icon set by <a href="http://www.pinvoke.com/">Yusuke Kamiyamane</a>; country flags by <a href="http://www.famfamfam.com/lab/icons/flags/">famfamfam</a> </p>
