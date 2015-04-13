import moviepy.editor as mpy
from moviepy.video.tools.cuts import FramesMatches

y = 'lrJRpqE1J2o'
f = 'boob'

# Get the video from youtube, save it as "hamac.mp4"
# mpy.download_webfile(y, "{0}.mp4".format(f))

clip = mpy.VideoFileClip("{0}.mp4".format(f)).resize(width=400)
matches = FramesMatches.from_clip(clip, 40, 3) # loose matching
# find the best matching pair of frames > 1.5s away
best = matches.filter(lambda x: x.time_span > 3).best()
# Write the sequence to a GIF (with speed=30% of the original)
final = clip.subclip(best.t1, best.t2).speedx(0.5)
final.write_gif("{0}.gif".format(f), fps=20)