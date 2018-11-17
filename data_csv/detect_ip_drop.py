import sys, os, pickle

def mac_to_id(mac):
	return int(mac.split(':')[-1], 16) - 1

def ip_to_id(ip):
	return int(ip.split('.')[-1]) - 1

def main(input_file):
	data = pickle.load(open(input_file, 'rb'))
	sources = []
	for p in data:
		if 'IPv4' in p:
			if mac_to_id(p['MAC']['src']) == ip_to_id(p['IPv4']['src']):
				sources.append(p)
	sinks = []
	for p in data:
		if 'IPv4' in p:
			if mac_to_id(p['MAC']['dst']) == ip_to_id(p['IPv4']['dst']):
				sinks.append(p)
	print("{} sources...".format(len(sources)))
	print("{} sinks...".format(len(sinks)))
	if len(sinks) < len(sources):
		print("{} IP packets were droped.".format(len(sources) - len(sinks)))
	
if __name__ == "__main__":
	try:
		input_file = sys.argv[1]
	except:
		print("python detect_ip_drop.py <path_to_data>")
		exit(-1)
	if not os.path.isfile(input_file):
		print("Invalid input file path!")
		exit(-1)
	main(input_file)