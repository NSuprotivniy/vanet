import sys, re, glob
import pandas as pd
import numpy as np

def get_packets(name):

    packets = list()
    max_node = 0
    max_time = 0

    for file in glob.glob(name + '*.routes'):
        
        handle = open(file, 'r')
        data = handle.read()
        handle.close()

        _nodes = re.split('\n\n', data);
        _nodes.pop()

        for node in _nodes:

            _strs = re.findall('(\d{1,3}(?:\.\d{1,3}){3})\s+\
\d{1,3}(?:\.\d{1,3}){3}\s+\
\d{1,3}(?:\.\d{1,3}){3}\s+\
\w+\s+\
-?\d+\.\d+\s+\
(\d+)', node)

            strings = list()
            for _str in _strs:
                strings.append(dict(zip(('Destination', 'Hops'), _str)))
		
            header = re.findall('Node:\s+(\d+)\s+Time:\s+(\d+)', node)

            max_node = max(max_node, int(header[0][0]))
            max_time = max(max_time, int(header[0][1]))

            for _str in strings:
                _str['Node'] = int(header[0][0])
                _str['Time'] = int(header[0][1])
                packets.append(_str)	

    return packets, max_node + 1, max_time

def packets_second_in(packets, max_node, max_time):

    data = dict()
    
    for packet in packets:

        node = packet.get('Node', None)

        if node != None:
            
            if data.get(node, None) == None:
                data[node] = [0] * max_time

            time = packet.get('Time') - 1
            data.get(node)[time] = data.get(node)[time] + 1
    
    data2 = dict()
    keys = ( 'sum', 'max', 'min', 'average' )
    for key in keys:
        data2[key] = dict()

    for d in data:
        data2.get('sum')[d] = sum(data.get(d))
        data2.get('max')[d] = max(data.get(d))
        data2.get('min')[d] = min(data.get(d))
        data2.get('average')[d] = float(sum(data.get(d))) / float(len(data.get(d)))

    return data, data2

def packets_second_out(packets, max_node, max_time):

    data = dict()
    
    for packet in packets:

        dest = packet.get('Destination', None)

        if dest != '127.0.0.1' and dest != '10.1.2.255':
            
            if data.get(dest, None) == None:
                data[dest] = [0] * max_time

            time = packet.get('Time') - 1
            data.get(dest)[time] = data.get(dest)[time] + 1
    
    data2 = dict()
    keys = ( 'sum', 'max', 'min', 'average' )
    for key in keys:
        data2[key] = dict()

    for d in data:
        data2.get('sum')[d] = sum(data.get(d))
        data2.get('max')[d] = max(data.get(d))
        data2.get('min')[d] = min(data.get(d))
        data2.get('average')[d] = float(sum(data.get(d))) / float(len(data.get(d)))

    return data, data2

def hops_second(packets, max_node, max_time):

    data = dict()
    keys = ( 'max', 'average', 'count' )

    for key in keys:
        data[key] = [0] * max_time
    data['min'] =  [sys.maxint] * max_time  

    for packet in packets:

        hops = int(packet.get('Hops'))
        if hops == 0:
            continue

        time = packet.get('Time') - 1
        data.get('max')[time] = max(hops, data.get('max')[time])
        data.get('min')[time] = min(hops, data.get('min')[time])
        data.get('average')[time] = data.get('average')[time] + hops
        data.get('count')[time] = data.get('count')[time] + 1

    print max_time, data.get('count')
    for i in range(max_time):
        data.get('average')[i] = float( data.get('average')[i]) / float(data.get('count')[i] )
        data.get('average')[i] = float( '{:.3f}'.format( data.get('average')[i]) )

    return data

if len(sys.argv) == 1 or sys.argv[1] == 'help':
    print ('enter attack name as first argument!')
else:
    packets, max_node, max_time = get_packets(sys.argv[1])

    packets_in, packets_in_stat = packets_second_in(packets,max_node,max_time)
    packets_in, packets_in_stat = pd.DataFrame(packets_in), pd.DataFrame(packets_in_stat)

    packets_out, packets_out_stat = packets_second_out(packets,max_node,max_time)
    packets_out, packets_out_stat = pd.DataFrame(packets_out), pd.DataFrame(packets_out_stat)

    #hops = pd.DataFrame(hops_second(packets,max_node,max_time))

    packets_in.to_csv(sys.argv[1] + '_packets_in.csv', index=False) # strings - seconds, columns - nodes
    packets_in_stat.to_csv(sys.argv[1] + '_packets_in_stat.csv', index=False) # strings - nodes
    packets_out.to_csv(sys.argv[1] + '_packets_out.csv', index=False) # strings - seconds, columns - nodes
    packets_out_stat.to_csv(sys.argv[1] + '_packets_out_stat.csv', index=False) # strings - nodes
    #hops.to_csv(sys.argv[1] + '_hops.csv', index=False) # strings - seconds

