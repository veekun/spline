ul.forum-hierarchy { margin: 0.25em 1em; color: #202020; }
ul.forum-hierarchy li { margin: 0.25em; }

.forum-access-level { font-size: 0.8em; padding: 0.25em 0.625em; font-style: italic; color: #606060; }
.forum-access-level img { vertical-align: middle; }

table.forum-list { width: 100%; margin-top: 0.5em; }
table.forum-list .header-row th { vertical-align: middle; }
table.forum-list .name { text-align: left; }
table.forum-list td.name a { display: block; font-size: 1.5em; padding: 0.33em; }
table.forum-list td.name .forum-description { padding: 0.33em 0.5em; color: #404040; }
table.forum-list .last-post { width: 20em; }
table.forum-list td.last-post { line-height: 1.33; text-align: left; vertical-align: top; }
table.forum-list .stats { width: 8em; text-align: center; }
table.forum-list td.stats { line-height: 1.33; vertical-align: top; }
table.forum-list td.stats.verylow   { font-weight: bold; color: #aaaaaa; }
table.forum-list td.stats.low       { font-weight: bold; color: #aa5555; }
table.forum-list td.stats.okay      { font-weight: bold; color: #aa9555; }
table.forum-list td.stats.high      { font-weight: bold; color: #78aa55; }
table.forum-list td.stats.veryhigh  { font-weight: bold; color: #559eaa; }
table.forum-list td.stats.whoanelly { font-weight: bold; color: #6855aa; }

.forum-post-container { }
.forum-post { position: relative; margin: 1em 0; background: #fcfcfc; -moz-border-radius: 1em; -webkit-border-radius: 1em; }
.forum-post .author { position: absolute; top: 2.2em; right: 0; bottom: 0; width: 16em; padding: 0 1em; margin: 1em 0; border-left: 1px solid #b4c7e6; }
.forum-post .author .name { display: block; font-size: 1.5em; }
.forum-post .author .name .user-color-bar { display: block; font-size: 0.67em; width: auto; }
.forum-post .author .avatar { margin-bottom: 1em; }
.forum-post .author .avatar img { -moz-box-shadow: 0 0 2px black; }
.forum-post .meta { padding: 0.5em 1em; border: 1px solid #b4c7e6; background: url(${h.static_uri('local', 'images/layout/th-background.png')}) left bottom repeat-x; -moz-border-radius-topleft: 0.5em; -moz-border-radius-topright: 0.5em; -webkit-border-top-left-radius: 0.5em; -webkit-border-top-right-radius: 0.5em; }
.forum-post .content { min-height: 12em; margin-right: 18.5em; padding: 1em; }
.forum-post:nth-child(2n) { background: #f4f4f4; }
