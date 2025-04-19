import ffmpeg # requires pip install ffmpeg-python (NOT ffmpeg!)
import time
import os

inFile = r"D:\Videos\Novatek\EVENT\system\scriptedthings\pool Rene.mp4" # 1920x1080

ouFile = f"{inFile}.output.mp4" # outputfile get's deleted before creation!
loFile = r"arrow.mp4" # 512x512

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
	output.run(quiet=True)
	if os.path.isfile(target_file + '.tm1'):
		os.rename(target_file, target_file + '.tm2')
		with open(target_file + '.txt', 'w') as f:
			for argno in range(1, 3):
				f.write(f"file '{target_file}.tm{argno}'\n")
		ffmpeg.input(target_file + '.txt', format='concat', safe=0).output(target_file, c='copy').run(quiet=True)
		delete_temp_files(target_file)

def append_video_only(in_file, out_file, start_time, duration):
	global counter, infoText
	counter += 1
	ff = ffmpeg.input(in_file, ss=start_time, t=duration)
	infoText = f"added {duration:.1f}s {start_time:.1f} to {start_time+duration:.1f} Video-Part {counter} only appending."
	append_or_create(ff.output(out_file, vcodec='h264_nvenc'), out_file)

def speed_manipulation(in_file, out_file, start_time, duration, speed_factor, logo_file):
	global counter, infoText
	counter += 1
	ff = ffmpeg.input(in_file, ss=start_time, t=duration)
	ff = ff.filter('setpts', f'{1/speed_factor}*PTS') # speed up main video
	if logo_file:
		infoText = f"added {duration/speed_factor:.1f}s {start_time:.1f} to {start_time+duration:.1f} Video-Part {counter} with a Logo and Speed {speed_factor:.1f}."
		logo = (
			ffmpeg.input(logo_file, stream_loop=-1, ss=0, t=duration/speed_factor)  # Logo must be calculated with speedfactor
			.video
			.filter('fade', t='in' , st=0                          , d=0.6) # start at 0 seconds for 0.6 seconds
			.filter('fade', t='out', st=(duration/speed_factor)-0.6, d=0.6) # Logo must be calculated with speedfactor
			.filter('chromakey', '0xffffff', 0.05, 0.03)
		)
		if (speed_factor < 1):
			logo = ffmpeg.hflip(logo)
		ff = ff.overlay(logo, x = 704, y = 538,  enable=f'between(t,0,{start_time+duration})' )
	else:
		infoText = f"added {duration/speed_factor:.1f}s {start_time:.1f} to {start_time+duration:.1f} Video-Part {counter} without Logo and Speed {speed_factor:.1f}."
	append_or_create(ff.output(out_file, vcodec='h264_nvenc'), out_file)

counter = 0
infoText = ""

delete_file_if_exists(ouFile)

print("\r\nstarting work.\r\n")
start = time.time()

# maybe make this part more configureable like a json-file with a commandlist...

speed_manipulation(inFile, ouFile, 0, 6, 3, loFile) # 3x speed 6 Seconds (2 in final) + Logo
append_video_only(inFile, ouFile, 6, 2) # 2 Seconds normal speed
speed_manipulation(inFile, ouFile, 8, 0.4, 0.2, loFile) # 1/5th speed with logo (mirrored) for 0.4 Seconds (2 Seconds in final)
speed_manipulation(inFile, ouFile, 8.4, 1.1, 0.2, None) # 1/5th speed without logo (mirrored) for 1.1 Seconds (5.5 Seconds in final)
# total final: 2 + 2 + 2 + 5.5 = 11.5 Seconds

end = time.time()

print("\r\nwriting finished.")
print(f"duration: {end - start:.1f} s")
