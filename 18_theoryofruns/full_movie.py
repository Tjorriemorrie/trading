import moviepy.editor as mp
from moviepy.video.tools.cuts import FramesMatches
from moviepy.video.fx.all import crop

y = 'lrJRpqE1J2o'
f = 'catyawn'

if False:

    # Get the video from youtube, save it as "hamac.mp4"
    # mp.download_webfile(y, "{0}.mp4".format(f))

    clip = mp.VideoFileClip("{0}.mp4".format(f))

    matches = FramesMatches.from_clip(clip.resize(width=120), 5, 2)
    print '{0} selected scenes'.format(len(matches))

    # (Optional) Save the matches for later use.
    matches.save("{0}_matches.txt".format(f))
    print 'matches saved'

else:
    clip = mp.VideoFileClip("{0}.mp4".format(f))
    print 'loaded clip'

    matches = FramesMatches.load("{0}_matches.txt".format(f))
    print '{0} matches'.format(len(matches))

    selected_scenes = matches.select_scenes(
        match_thr=2,
        min_time_span=0.5,
        nomatch_thr=4,
        time_distance=0.5,
    )
    print '{0} selected scenes'.format(len(selected_scenes))

    clip_edited = crop(
        clip,
        x_center=100,
        y_center=100,
        width=50,
        height=50,
    )
    print 'clip edited'

    selected_scenes.write_gifs(clip_edited, f)
    print 'selected scenes written'