import sys, os

def main(input):
	with open(input, 'r') as f:
		data = f.read()
	data = data.split('meta-info="')
	meta_info = []
	data.pop(0)
	for b in data:
		meta_info.append(b.split('"')[0])
	protos = []
	for m in meta_info:
		slt = m.split('ns3::')
		slt.pop(0)
		for s in slt:
			proto = s.split(' ')[0]
			if proto not in protos:
				protos.append(proto)
	print("Found {} protocols in dump file...".format(len(protos)))
	print("Protocols list: {}".format(protos))
	
if __name__ == "__main__":
	try:
		input = sys.argv[1]
	except:
		print("python check_protocols.py <path_to_ns3_xml>")
		exit(-1)
	if not os.path.isfile(input):
		print("Invalid input file path!")
		exit(-1)
	main(input)