#!/usr/bin/env python

import os
import sys

mobileJS = """\
    $( document ).on( "pageinit", "[data-role='page'].album-page", function() {
        var page = "#" + $( this ).attr( "id" ),
            // Get filenames of next, prev pages stored in data-next, data-prev
            next = $( this ).jqmData( "next" ),
            prev = $( this ).jqmData( "prev" );
        
        // prefetch next, prev images and set up swiping, buttons
        if ( next ) {
            $.mobile.loadPage( "#" + next );
            $( document ).on( "swipeleft", page, function() {
                $.mobile.changePage( "#" + next );
            });
            $( ".control .next", page ).on( "click", function() {
                $.mobile.changePage( "#" + next );
            });
        }
        else {
            $( ".control .next", page ).addClass( "ui-disabled" );
        }
        // for prev, we set data-dom-cache="true" so there is no need to prefetch
        if ( prev ) {
            $( document ).on( "swiperight", page, function() {
                $.mobile.changePage( "#" + prev, { reverse: true } );
            });
            $( ".control .prev", page ).on( "click", function() {
                $.mobile.changePage( "#" + prev, { reverse: true } );
            });
        }
        else {
            $( ".control .prev", page ).addClass( "ui-disabled" );
        }
    });
"""


mobileCSS = """\
    /* Background settings */
    .album-page {
        background-size: contain;
        background-position: center center;
        background-repeat: no-repeat;
    }
    /* Transparent footer */
    .ui-footer {
        background: none;
        border: none;
    }
    /* The footer won't have a height because there are only two absolute positioned elements in it.
    So we position the buttons from the bottom. */
    .control.ui-btn-left, .exif-btn.ui-btn-right {
        top: auto;
        bottom: 7px;
        margin: 0;
    }
    /* Custom styling for the exif source */
    small {
        font-size: .75em;
        color: #666;
    }
    /* Prevent text selection while swipe with mouse */
    .ui-header, .ui-title, .control .ui-btn, .exif-btn {
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        -o-user-select: none;
        user-select: none;
    }"""

headHTML = """\
<head>
    <meta charset="utf-8">
    <title>%(title)s</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://code.jquery.com/mobile/1.2.0/jquery.mobile-1.2.0.min.css">
    <script src="https://code.jquery.com/jquery-1.7.1.min.js"></script>
    <script>
        // Bind to "mobileinit" before you load jquery.mobile.js
        // Set the default transition to slide
        $(document).on( "mobileinit", function() {
            $.mobile.defaultPageTransition = "slide";
        });    
    </script>
    <script src="mobile.js"></script>
    <script src="https://code.jquery.com/mobile/1.2.0/jquery.mobile-1.2.0.min.js"></script>
    <style>%(imagemap)s </style>
    <link rel="stylesheet" href="mobile.css">
</head>
"""

bodyHTML = """\
<body>
<div data-role="page" %(idattr)s class="album-page" data-dom-cache="true" data-theme="a" %(prevattr)s %(nextattr)s >
    <div data-role="header" data-position="fixed" data-fullscreen="true" data-id="hdr" data-tap-toggle="false">
        <h1>%(heading)s</h1>
        <a href="backlinks" data-ajax="false" data-direction="reverse" data-icon="delete" data-iconpos="notext" data-shadow="false" data-icon-shadow="false">Back</a>
    </div>
    <div data-role="content">
        <div id="exif" class="exif ui-content" data-role="popup" data-position-to="window" data-tolerance="50,30,30,30" data-theme="d">
            <a href="#" data-rel="back" data-role="button" data-theme="a" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
            <p>TODO: insert ISO, Aperture, Shutter, flash info, metering, autofocus, focal length etc stuff here...</p>
        </div>
    </div>
    <div data-role="footer" data-position="fixed" data-fullscreen="true" data-id="ftr" data-tap-toggle="false">
        <div data-role="controlgroup" class="control ui-btn-left" data-type="horizontal" data-mini="true">
            <a href="#" class="prev" data-role="button" data-icon="arrow-l" data-iconpos="notext" data-theme="d">Previous</a>
            <a href="#" class="next" data-role="button" data-icon="arrow-r" data-iconpos="notext" data-theme="d">Next</a>
        </div>
        <a href="#exif" data-rel="popup" class="exif-btn ui-btn-right" data-role="button" data-icon="info" data-iconpos="left" data-theme="d" data-mini="true">EXIF</a>
    </div>
</div><!-- /page -->
</body>
"""

pageHTML = """\
<div data-role="page" %(idattr)s class="album-page" data-dom-cache="true" data-theme="a" %(prevattr)s %(nextattr)s >
    <div data-role="header" data-position="fixed" data-fullscreen="true" data-id="hdr" data-tap-toggle="false">
        <h1>%(heading)s</h1>
        <a href="backlinks" data-ajax="false" data-direction="reverse" data-icon="delete" data-iconpos="notext" data-shadow="false" data-icon-shadow="false">Back</a>
    </div>
    <div data-role="content">
        <div id="exif" class="exif ui-content" data-role="popup" data-position-to="window" data-tolerance="50,30,30,30" data-theme="d">
            <a href="#" data-rel="back" data-role="button" data-theme="a" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
            <p>TODO: insert ISO, Aperture, Shutter, flash info, metering, autofocus, focal length etc stuff here...</p>
        </div>
    </div>
    <div data-role="footer" data-position="fixed" data-fullscreen="true" data-id="ftr" data-tap-toggle="false">
        <div data-role="controlgroup" class="control ui-btn-left" data-type="horizontal" data-mini="true">
            <a href="#" class="prev" data-role="button" data-icon="arrow-l" data-iconpos="notext" data-theme="d">Previous</a>
            <a href="#" class="next" data-role="button" data-icon="arrow-r" data-iconpos="notext" data-theme="d">Next</a>
        </div>
        <a href="#exif" data-rel="popup" class="exif-btn ui-btn-right" data-role="button" data-icon="info" data-iconpos="left" data-theme="d" data-mini="true">EXIF</a>
    </div>
</div><!-- /page %(idattr)s -->
"""

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imagefile",help="path to images to include in output HTML page", nargs="*")
    args = parser.parse_args()

    images = args.imagefile
    n = len(images)

    # create support files
    file("mobile.js", "w").write(mobileJS)
    file("mobile.css", "w").write(mobileCSS)
    outfile = "mobile.html"

    def makePageId(i):
        return "p%d" % i

    def makeAttrs(i, n):
        idattr='id="%s"' % makePageId(i)
        prevattr = nextattr = ''
        if i > 0:
            prevattr = 'data-prev="%s"' % makePageId(i - 1)
        if i < n-1:
            nextattr = 'data-next="%s"' % makePageId(i + 1)
        return (idattr, prevattr, nextattr)

    # make mobile page
    imagemap = ["/* Set the background image sources */"]
    imagemap.extend([ "#%s { background-image: url(%s); }" % (makePageId(i_ind), images[i_ind]) for i_ind in range(n) ])
    
    with file(outfile, 'w') as o:
        o.write("<!doctype html><html>")
        o.write(headHTML % {'title': "%d images" % n,
                            'imagemap':'\n'.join(imagemap) })
        o.write("<body>")
        for i in range(n):
            idattr, prevattr, nextattr = makeAttrs(i, n)
            heading = os.path.basename(images[i]) + ' (%d of %d)' % (i+1, n)
            o.write(pageHTML % {'pagename':os.path.basename(images[i]),
                                'heading':heading,
                                'idattr': idattr,
                                'prevattr':prevattr,
                                'nextattr':nextattr
                               })
        o.write("</body></html>")
    print "Wrote", outfile

