.frontpage-update { position: relative; overflow: auto; margin: 1em 0; background: #f4f4f4; -moz-border-radius: 1em; -webkit-border-radius: 1em; }
.frontpage-update:nth-child(2n) { background: #f0f0f0; }
.frontpage-update .header { white-space: nowrap; padding: 0.5em 1em; border: 1px solid #b4c7e6; background: url(${h.static_uri('local', 'images/layout/th-background.png')}) left bottom repeat-x; -moz-border-radius-topleft: 1em; -moz-border-radius-topright: 1em; -webkit-border-top-left-radius: 0.5em; -webkit-border-top-right-radius: 0.5em; }
.frontpage-update .header .category { float: left; font-size: 1.33em; margin-right: 0.25em; font-style: italic; color: #404040; vertical-align: bottom; }
.frontpage-update .header .category a { font-weight: normal; }
.frontpage-update .header .category img { vertical-align: bottom; }
.frontpage-update .header .date { float: right; white-space: nowrap; line-height: 1.33; margin-left: 0.33em; vertical-align: bottom; }
.frontpage-update .header .title { overflow: hidden; font-size: 1.33em; height: 1em; vertical-align: bottom; text-overflow: ellipsis; font-weight: bold; color: #303030; }
.frontpage-update .avatar { float: right; margin: 1em; }
.frontpage-update .avatar img { -moz-box-shadow: 0 0 2px black; }
.frontpage-update .content { padding: 1em; line-height: 1.33; }
.frontpage-update .content.has-comments { padding-bottom: 3.5em; }
.frontpage-update .comments { position: absolute; bottom: 0; left: 0; padding: 1em; }

table.frontpage-repository { width: 100%; }
table.frontpage-repository tr.frontpage-repository-header { background: transparent !important; }
table.frontpage-repository th { font-size: 1.25em; padding: 0.5em 0 0; border-bottom: 1px solid #2457a0; text-align: left; font-style: italic; }
table.frontpage-repository tr:first-child th { padding-top: 0; }
table.frontpage-repository td.hash { width: 6em; text-align: center; font-family: monospace; }
table.frontpage-repository td.author { width: 10em; }
table.frontpage-repository td.time { width: 12em; }
