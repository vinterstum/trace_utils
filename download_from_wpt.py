import argparse
import urllib, json
import urlparse
import os.path

parser = argparse.ArgumentParser(description='Download traces from Webpagetest')
parser.add_argument('output_path',
                   help='Output path')
args = parser.parse_args()

output_path = os.path.abspath(args.output_path)
print 'Output path: %s' % output_path

url = 'http://www.webpagetest.org/jsonResult.php?test=160421_5W_e5501a872437844eb053b831d3f0f17f'

print 'Downloading results data from %s...' % url
response = urllib.urlopen(url)
data = json.load(response)

#print json.dumps(data, indent=4, sort_keys=True)

for k,v in data['data']['runs'].iteritems():
  for a,b in v.iteritems():
    trace_url = b['rawData']['trace']
    parsed_url = urlparse.urlparse(trace_url)
    query = urlparse.parse_qsl(parsed_url.query)
    file_name = os.path.join(output_path, query[2][1])
    print 'Downloading %s to %s...' % (trace_url, file_name)
    urllib.urlretrieve(trace_url, file_name)
