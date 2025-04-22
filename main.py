import ffmpeg # requires pip install ffmpeg-python (NOT ffmpeg!)
import time
import os

inFile = r"D:\Videos\Novatek\EVENT\system\scriptedthings\pool Rene2.mp4" # 1920x1080
ouFile = f"{inFile}.output.mp4" # outputfile get's deleted before creation!
loFile = r"arrow.mp4" # 512x512
audioOff = False
#audioOff = True
#vCodec='h264_nvenc' # fast CPU
#vCodec='hevc_nvenc' # fast GPU
#vCodec='libvpx-vp9' # extreme HQ (10x calculationtime)
vCodec='libx265' # HQ, (2x calculationtime)
outputWidth = 1980 # new Option - Change final Video Output to a different Resolution (Aspect Ratio stays the same)
doDebug = False # for seeing ffmpeg errors

def delete_file_if_exists(myfile):
	if os.path.isfile(myfile):
		unchecked = True
		while unchecked:
			try:
				os.remove(myfile)
				unchecked = False
			except (IOError, PermissionError):
				input(f"File {myfile} not Deleteable, close Player and press enter.")

def delete_temp_files(target_file):
	delete_file_if_exists(target_file + '.txt')
	delete_file_if_exists(target_file + '.tm1')
	delete_file_if_exists(target_file + '.tm2')

def append_or_create(output, target_file):
	global infoText
	print(infoText)
	delete_temp_files(target_file)
	if os.path.isfile(target_file):
		os.rename(target_file, target_file + '.tm1')
	output.run(quiet=not doDebug)
	if os.path.isfile(target_file + '.tm1'):
		os.rename(target_file, target_file + '.tm2')
		with open(target_file + '.txt', 'w') as f:
			for argno in range(1, 3):
				f.write(f"file '{target_file}.tm{argno}'\n")
		ffmpeg.input(target_file + '.txt', format='concat', safe=0).output(target_file, c='copy').run(quiet=not doDebug)
		delete_temp_files(target_file)

def append_video_only(in_file, out_file, start_time, duration):
	global counter, infoText, audioOff, vCodec, outputWidth
	counter += 1
	ff = ffmpeg.input(in_file, ss=start_time, t=duration)
	infoText = f"added {duration:.1f}s {start_time:.1f} to {start_time+duration:.1f} Video-Part {counter} only appending."
	video = ff.video
	audio = ff.audio
	if outputWidth:
		video = video.filter('scale', outputWidth, -1)
	if audioOff:
		append_or_create(ffmpeg.output(video, out_file, vcodec=vCodec), out_file)
	else:
		append_or_create(ffmpeg.output(video, audio, out_file, vcodec=vCodec, acodec='aac'), out_file)

def speed_manipulation(in_file, out_file, start_time, duration, speed_factor, logo_file, width = 512, xpos = 704, ypos = 538, chomakey = '0xffffff'):
	global counter, infoText, audioOff, vCodec, outputWidth
	counter += 1
	ff = ffmpeg.input(in_file, ss=start_time, t=duration)
	video = ff.video.filter('setpts', f'{1/speed_factor}*PTS') # speed up main video
	if outputWidth:
		video = video.filter('scale', outputWidth, -1)
	#Audio adjustment
	if not audioOff:
		if 0.5 <= speed_factor <= 2.0:
			audio = ff.audio.filter('atempo', speed_factor)
		else:
			# Trick für >2.0 oder <0.5: aufteilen in erlaubte Schritte
			tempo_parts = []
			s = speed_factor
			while s > 2.0:
				tempo_parts.append(2.0)
				s /= 2.0
			while s < 0.5:
				tempo_parts.append(0.5)
				s *= 2.0
			tempo_parts.append(s)
			audio = ff.audio
			for tempo in tempo_parts:
				audio = audio.filter('atempo', tempo)
	if logo_file:
		infoText = f"added {duration/speed_factor:.1f}s {start_time:.1f} to {start_time+duration:.1f} Video-Part {counter} with a Logo and Speed {speed_factor:.1f}."
		logo = (
			ffmpeg.input(logo_file, stream_loop=-1, ss=0, t=duration/speed_factor)  # Logo must be calculated with speedfactor
			.video
			.filter('fade', t='in' , st=0                          , d=0.6) # start at 0 seconds for 0.6 seconds
			.filter('fade', t='out', st=(duration/speed_factor)-0.6, d=0.6) # Logo must be calculated with speedfactor
			
			.filter('scale', width, -1)
		)
		if chomakey:
			logo = logo.filter('chromakey', chomakey, 0.05, 0.03)

		if (speed_factor < 1):
			logo = ffmpeg.hflip(logo)
		video = video.overlay(logo, x = xpos, y = ypos, enable=f'between(t,0,{start_time+duration})' )
	else:
		infoText = f"added {duration/speed_factor:.1f}s {start_time:.1f} to {start_time+duration:.1f} Video-Part {counter} without Logo and Speed {speed_factor:.1f}."
	if audioOff:
		append_or_create(ffmpeg.output(video, out_file, vcodec=vCodec), out_file)
	else:
		append_or_create(ffmpeg.output(video, audio, out_file, vcodec=vCodec, acodec='aac'), out_file)

counter = 0
infoText = ""
print("\r\nstarting work.\r\n")
start = time.time()

ouFile = r"D:\Videos\Novatek\EVENT\system\scriptedthings\2024-06-02 20.27.20 NFS.mp4" # 1920x1080
delete_file_if_exists(ouFile)

# maybe make this part more configureable like a json-file with a commandlist...


inFile = r"D:\Videos\Novatek\EVENT\schnelles fahren\2024-06-02 20.27.20 A 160+.MP4" # 2560 px width origin
# more Options: Overlay-Video with changed Resolution at x/y position, adjustable or no chroma-key
# Mirror (Back) Camera downscaled at top center position without chromakey
speed_manipulation(inFile, ouFile, 0, 40, 1, r"D:\Videos\Novatek\EVENT\schnelles fahren\2024-06-02 20.27.20 B 160+.MP4", 720, outputWidth/2-720/2, 30, None)
exit()


pos = 17
dur = 55
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 1:12 / 72
pos += dur
dur = 1
speed_manipulation(inFile, ouFile, pos, dur, 2, None)
pos += dur
speed_manipulation(inFile, ouFile, pos, dur, 2, None)
# 1:14 / 74
pos += dur
dur = 6
append_video_only(inFile, ouFile, pos, dur) # 2 Seconds normal speed
# 1:20 / 80
pos += dur
dur = 20
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 1:40 / 100
pos += dur
dur = 5
append_video_only(inFile, ouFile, pos, dur)
# 1:45 / 105
pos += dur
dur = 10
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 1:55 / 115
pos += dur
dur = 7
append_video_only(inFile, ouFile, pos, dur)
# 2:02 / 122
pos += dur
dur = 8
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 2:10 / 130
pos += dur
dur = 20
append_video_only(inFile, ouFile, pos, dur)
# 2:30 / 150
pos += dur
dur = 10
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 2:40 / 160
pos += dur
dur = 7
append_video_only(inFile, ouFile, pos, dur)
# 2:47 / 167
pos += dur
dur = 8
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 2:55 / 175
pos += dur
dur = 20
append_video_only(inFile, ouFile, pos, dur)
# 3:15 / 195
pos += dur
dur = 50
speed_manipulation(inFile, ouFile, pos, dur, 4, loFile)
# 4:05 / 245
pos += dur
dur = 55
append_video_only(inFile, ouFile, pos, dur)
# 5:00 / 300
pos += dur
dur = 35
speed_manipulation(inFile, ouFile, pos, dur, 4, loFile)
# 5:35 / 335
pos += dur
dur = 7
append_video_only(inFile, ouFile, pos, dur)
# 5:42 / 342
pos += dur
dur = 13
speed_manipulation(inFile, ouFile, pos, dur, 3, loFile)
# 5:55 / 355
pos += dur
dur = 6
append_video_only(inFile, ouFile, pos, dur)
# 6:01 / 361

end = time.time()

print("\r\nwriting finished.")
print(f"duration: {end - start:.1f} s")
