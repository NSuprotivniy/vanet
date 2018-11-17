import sys, os, pickle
import xml.etree.ElementTree as ET

class Ns3XmlParser:
	proto_dict = {
		'ns3::WifiMacHeader' : 'MAC',
		'ns3::LlcSnapHeader' : 'LLC',
		'ns3::ArpHeader' : 'ARP',
		'ns3::Ipv4Header' : 'IPv4',
		'ns3::UdpHeader' : 'UDP',
		'ns3::aodv::TypeHeader' : 'AODV_Type',
		'ns3::aodv::RrepHeader' : 'AODV_RREP',
		'ns3::aodv::RreqHeader' : 'AODV_RREQ',
		'ns3::aodv::RrepAckHeader' : 'AODV_RACK',
		'ns3::aodv::RerrHeader' : 'AODV_RERR',
		'ns3::Icmpv4Header' : 'ICMPv4_HEADER',
		'ns3::Icmpv4TimeExceeded' : 'ICMPv4_TE',
		'ns3::Icmpv4DestinationUnreachable' : 'ICMPv4_DU'
	}

	def __init__(self, file_path):
		try:
			self.xml_data = ET.parse(file_path)
		except ET.ParseError as e:
			with open(file_path, 'a') as f:
				f.write('</anim>')
			self.xml_data = ET.parse(file_path)
	
	def parse_nodes(self):
		nodes_tags = self.xml_data.findall('node')
		nodes_addresses_tags = self.xml_data.findall('nonp2plinkproperties')
		nodes_locations_tags = self.xml_data.findall('nu')
		nodes = {}
		for node_tag in nodes_tags:
			attributes = node_tag.attrib
			cur_node_id = int(attributes['id'])
			nodes[cur_node_id] = {}
			nodes[cur_node_id]['locations'] = {}
			nodes[cur_node_id]['locations'][0.0] = (float(attributes['locX']), float(attributes['locY']))
		for nodes_address_tag in nodes_addresses_tags:
			attributes = nodes_address_tag.attrib
			cur_node_id = int(attributes['id'])
			addresses = attributes['ipv4Address'].split('~')
			nodes[cur_node_id]['IPv4addr'] = addresses[0]
			nodes[cur_node_id]['MACaddr'] = addresses[1]
		for nodes_location_tag in nodes_locations_tags:
			attributes = nodes_location_tag.attrib
			if 'x' not in attributes:
				continue
			cur_node_id = int(attributes['id'])
			nodes[cur_node_id]['locations'][float(attributes['t'])] = (float(attributes['x']), float(attributes['y']))
		return nodes
		
	def parse_meta_info(self, meta_info):
		raw = {}
		for proto in Ns3XmlParser.proto_dict:
			if meta_info.find(proto) != -1:
				raw[Ns3XmlParser.proto_dict[proto]] = meta_info.split(proto+' (')[1].split(') ns3')[0]
		p = {}
		if 'MAC' in raw and 'LLC' in raw:
			p['MAC'] = {}
			p['MAC']['src'] = raw['MAC'].split('SA=')[1].split(',')[0]
			p['MAC']['dst'] = raw['MAC'].split('DA=')[1].split(',')[0]
			p['MAC']['type'] = int(raw['LLC'].split('type ')[1], 16)
		if 'ARP' in raw:
			p['ARP'] = {}
			if raw['ARP'].find('request') != -1:
				p['ARP']['type'] = 'request'
			else:
				p['ARP']['type'] = 'reply'
				p['ARP']['MAC_dst'] = raw['ARP'].split('dest mac: ')[1].split(' ')[0]
			p['ARP']['MAC_src'] = raw['ARP'].split('source mac: ')[1].split(' ')[0]
			p['ARP']['IP_src'] = raw['ARP'].split('source ipv4: ')[1].split(' ')[0]
			p['ARP']['IP_dst'] = raw['ARP'].split('dest ipv4: ')[1]
		if 'IPv4' in raw:
			p['IPv4'] = {}
			ipv4data = raw['IPv4'].split(' ')
			p['IPv4']['src'] = ipv4data[-3]
			p['IPv4']['dst'] = ipv4data[-1]
			p['IPv4']['proto'] = int(raw['IPv4'].split('protocol ')[1].split(' ')[0])
			p['IPv4']['ttl'] = int(raw['IPv4'].split('ttl ')[1].split(' ')[0])
			p['IPv4']['length'] = int(raw['IPv4'].split('length: ')[1].split(' ')[0])
		if 'UDP' in raw:
			p['UDP'] = {}
			p['UDP']['length'] = int(raw['UDP'].split('length: ')[1].split(' ')[0])
		if 'AODV_Type' in raw:
			p['AODV'] = {}
			p['AODV']['type'] = raw['AODV_Type']
		if 'AODV_RREP' in raw:
			p['AODV']['RREP'] = {}
			p['AODV']['RREP']['dst'] = raw['AODV_RREP'].split('destination: ipv4 ')[1].split(' ')[0]
			p['AODV']['RREP']['src'] = raw['AODV_RREP'].split('source ipv4 ')[1].split(' ')[0]
			p['AODV']['RREP']['SN'] = int(raw['AODV_RREP'].split('sequence number ')[1].split(' ')[0])
			p['AODV']['RREP']['lifetime'] = int(raw['AODV_RREP'].split('lifetime ')[1].split(' ')[0])
			p['AODV']['RREP']['acknowledgment'] = raw['AODV_RREP'].split('acknowledgment ')[1].split(' ')[0]
			p['AODV']['RREP']['flag'] = raw['AODV_RREP'].split('flag ')[1]
		if 'AODV_RREQ' in raw:
			p['AODV']['RREQ'] = {}
			p['AODV']['RREQ']['ID'] = int(raw['AODV_RREQ'].split('ID ')[1].split(' ')[0])
			p['AODV']['RREQ']['dst'] = raw['AODV_RREQ'].split('destination: ipv4 ')[1].split(' ')[0]
			p['AODV']['RREQ']['src'] = raw['AODV_RREQ'].split('source: ipv4 ')[1].split(' ')[0]
			p['AODV']['RREQ']['SN'] = int(raw['AODV_RREQ'].split('sequence number ')[1].split(' ')[0])
			p['AODV']['RREQ']['flags'] = raw['AODV_RREQ'].split('flags: ')[1]
		if 'AODV_RACK' in raw:
			pass # seems to be empty
		if 'AODV_RERR' in raw:
			p['AODV']['RERR'] = raw['AODV_RERR']
		if 'ICMPv4_HEADER' in raw:
			p['ICMPv4'] = {}
			p['ICMPv4']['type'] = int(raw['ICMPv4_HEADER'].split('type=')[1].split(',')[0])
			p['ICMPv4']['code'] = int(raw['ICMPv4_HEADER'].split('code=')[1])
		if 'ICMPv4_TE' in raw:
			p['ICMPv4']['data'] = raw['ICMPv4_TE']
		if 'ICMPv4_DU' in raw:
			p['ICMPv4']['data'] = raw['ICMPv4_DU']
		return p
			
	def parse_packets(self):
		packets_tags = self.xml_data.findall('pr')
		packets = []
		for packet_tag in packets_tags:
			packet = {}
			packet['timestamp'] = packet_tag.attrib['fbTx']
			packet['content'] = self.parse_meta_info(packet_tag.attrib['meta-info'])
			if len(packet['content']) > 0:
				packets.append(packet)
		return packets
	
	def parse(self):
		self.dataset = {}
		self.dataset['nodes'] = self.parse_nodes()
		self.dataset['packets'] = self.parse_packets()
		return self.dataset
		

def main(input_file, output):
	with open(input_file, 'r') as f:
		data = f.read()
	parser = Ns3XmlParser(input_file)
	dataset = parser.parse()
	pickle.dump(dataset, open(output, 'wb'))	
	
if __name__ == "__main__":
	try:
		input_file = sys.argv[1]
		output = sys.argv[2]
	except:
		print("python parse_xml.py <path_to_ns3_xml> <output>")
		exit(-1)
	if not os.path.isfile(input_file):
		print("Invalid input file path!")
		exit(-1)
	try:
		open(output, 'wb').close()
	except:
		print("Invalid output file path!")
		exit(-1)
	main(input_file, output)