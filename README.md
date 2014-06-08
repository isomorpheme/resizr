#Introduction
This is a WIP Reddit bot. Its purpose is to help people with requests for larger versions of images. It will try to a) resize the image itself and b) to look up larger versions.

#Outline
    1. Fetch recent posts from /r/WallpaperRequests and/or /r/PhotoshopRequest
        1.1. Use PRAW
    2. Look for titles which include something along the lines of "N x M" or "N by M"
        2.1. Match regex
        2.2. Add to dict
    3. Get image from posts. i.e. loop thru the dict and use the link of each post
        3.1 Directly, in case of direct link
            3.1.1. Download to tmp/
        3.2 Parse HTML, in case of indirect link (meh, prolly not gonna do that)
    4. Resize, using multiple different interps or repeat edge pixels (or try higher rez on google?)
        4.1. Nearest neighbour
        4.2. Bilinear/bicubic
        4.3. Repeat edges
            4.3.1 Horizontal
            4.3.2 Vertical
            4.3.3 Both
        4.4. Search higher res on google? - perhaps link to img search for that img if not satisfied
    5. Save resized image to tmp folder
    6. Upload all resizes to imgur.com
        6.1. Use imgur API
            6.1.1. Upload from tmp folder
    7. Whereof one cannot speak, thereof one must be silent. Wait, I mean- Make comment with links, disclaimer, etc.
        7.1 Use PRAW