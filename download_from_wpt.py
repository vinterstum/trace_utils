#!/usr/bin/python
# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
import urllib, json
import urlparse
import os.path
import zlib
import cloudstorage as gcs

# Deal with limited data at the time,
# metadata should virtually always come in one round.
CHUNKSIZE=10 * 1024


def PrintMetadata(file_response, out_file):
  d = zlib.decompressobj(zlib.MAX_WBITS|32)
  trace_chunk = file_response.read(CHUNKSIZE)

  raw_trace_chunk = d.decompress(trace_chunk)
  print raw_trace_chunk
  out_file.write(trace_chunk)

def Main():
  parser = argparse.ArgumentParser(description='Download traces from Webpagetest')
  parser.add_argument('output_path',
                     help='Output path')
  args = parser.parse_args()

  output_path = os.path.abspath(args.output_path)
  print 'Output path: %s' % output_path

  url = 'http://www.webpagetest.org/jsonResult.php?test=160421_5W_e5501a872437844eb053b831d3f0f17f'

  print 'Downloading results data from %s...' % url
  job_response = urllib.urlopen(url)
  job_data = json.load(job_response)

  #print json.dumps(data, indent=4, sort_keys=True)

  for k,v in job_data['data']['runs'].iteritems():
    for a,b in v.iteritems():
      trace_url = b['rawData']['trace']
      parsed_url = urlparse.urlparse(trace_url)
      query = urlparse.parse_qsl(parsed_url.query)
      file_name = os.path.join(output_path, query[2][1])
      print 'Downloading %s to %s...' % (trace_url, file_name)

      file_response = urllib.urlopen(trace_url)

      out_file = open(file_name, 'wb')

      PrintMetadata(file_response, out_file)
      out_file.write(file_response.read())
      out_file.close()
      #urllib.urlretrieve(trace_url, file_name)

if __name__ == '__main__':
  Main()
