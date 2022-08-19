# pregananant

Every week I took a picture of my partner to document her growing belly.
The three Python scripts in the root are made to view and filter, annotate, and create video segments of the photos of each week.
[`Dockerfile`] documents the requirements, and can be used to run the scripts (need display access to use the viewer).

There are redundant hard-coded values in the top of each Python script - these could of course be generalized in a separate configuration file, but I've already reached my goal of creating a video of the progress, so I'm not wasting time on that :)

How I use the scripts:

1. Place images in a directory (`./imgs` by default)
2. Run `./viewer.py`. This script creates annotations for every image and places them in `./metadata.json`. Use the viewer to look at the image, see that the right pregnancy week is calculated, and exclude and delete the images that we don't want included.
3. Run `./draw.py` to draw the pregnancy week number in the top center of each image. The images are by default stored in `./edited_imgs`, with the file name pattern `ww-nn.ext`, where `ww` is the pregnancy week number, `nn` is the ordering of the image for that week, and `ext` is the file extension (e.g., `.jpg`).
4. Run `./video.py` to generate a video sequence for every week.
5. Use a video editor to stich the sequences together.

Due to privacy concerns, I will not post the result here, but I think it turned out well :)
