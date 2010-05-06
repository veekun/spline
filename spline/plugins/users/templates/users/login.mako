<%inherit file="/base.mako" />
<%def name="title()">Log in</%def>

<h1>Log in with OpenID</h1>

% if c.error:
<p class="error">${c.error}</p>
% endif

${h.form(url(controller='accounts', action='login_begin'), id='user')}
    <img src="${h.static_uri('spline', 'icons/openid.png')}">
    <input type="text" name="openid" size="30" value="${c.attempted_openid or ''}">
    <input type="submit" value="Log in">
${h.end_form()}


<h1>Oh my god what is this I am so confused</h1>

<p>Sorry!  Let me explain real quick.</p>

<p>Instead of having to register with a username and password on every site, the idea of <a href="https://openid.net/">OpenID</a> is that you register on <em>one</em> site, and then use <em>that</em> to log in everywhere else.</p>

<p>You don't need a separate ID card for everything you do in real life, because you can show a government ID, and the government confirms that they already know who you are.  This is pretty much the same thing.</p>

<p>Enter the URL to a site you own in the login box, and I'll go ask that site if it knows who you are.  (Most sites will also ask you to confirm that you want to login here.)  If it says yes, you're logged in here.</p>

<p>There's no registration, either; just log in, and you'll be registered.</p>

<p>Here are some common sites that support OpenID login:</p>

<dl>
    <dt>LiveJournal</dt>
    <dd>http://<code>username</code>.livejournal.com/</dd>
    <dt>AOL/AIM</dt>
    <dd>http://openid.aol.com/<code>screenname</code></dd>
    <dt>Blogger</dt>
    <dd>http://<code>blogname</code>.blogspot.com/</dd>
    <dt>Flickr</dt>
    <dd>http://www.flickr.com/<code>username</code></dd>
    <dt>Yahoo!</dt>
    <dd>http://www.yahoo.com/</dd>
    <dt>Google</dt>
    <dd>
        http://www.google.com/accounts/o8/id <br>
        You can also use http://www.google.com/profiles/<code>username</code>, but first you have to enable it at the bottom of <a href="http://www.google.com/profiles/me/editprofile?edit=t">this page</a>.
    </dd>
</dl>

<p>Yeah, Yahoo! and Google are kinda weird.  Wikipedia has a <a href="http://en.wikipedia.org/wiki/List_of_OpenID_providers">more comprehensive list</a>.</p>

<p>If you don't use any of these sites, you can also get a login from a <a href="http://openid.net/get-an-openid">dedicated OpenID provider</a>.</p>
