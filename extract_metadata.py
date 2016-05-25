#!/usr/bin/python
# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse
#import urllib, json
#import urlparse
import os.path
import zlib
import json

# Deal with limited data at the time,
# metadata should ideally always come in the first round.
CHUNKSIZE=1024

class MetadataDetector:
  def __init__(self):
    self.metadata_detected = False

  def __call__(self, parsed_dict):
    if 'metadata' in parsed_dict:
      self.metadata_detected = True
    return parsed_dict

def PrintMetadata(file_response, out_buffer):
  decompressor = zlib.decompressobj(zlib.MAX_WBITS|32)

  initial_chunksize = CHUNKSIZE
  FOUND_METADATA = False

  metadata_detector = MetadataDetector()
  full_trace = ''
  partial_json = None
  while not metadata_detector.metadata_detected:
    trace_chunk = file_response.read(initial_chunksize)
    if not trace_chunk:
      break

    uncompressed_trace_chunk = decompressor.decompress(trace_chunk)
    if not uncompressed_trace_chunk:
      break

    out_buffer.write(trace_chunk)
    initial_chunksize = initial_chunksize * 2
    full_trace += uncompressed_trace_chunk

    try:
      partial_json = json.loads(full_trace, object_hook=metadata_detector)
    except ValueError:
      pass

  if partial_json and 'metadata' in partial_json:
    for key, value in partial_json['metadata'].iteritems():
      print '%s: %s' % (key, value)

def ImportFromLocalFolder(local_path, output_path):
  print 'Importing files from %s to %s' % (local_path, output_path)

  for f in os.listdir(local_path):
    in_path = os.path.join(local_path, f)
    out_path = os.path.join(output_path, f)
    print 'Importing %s to %s' % (in_path, out_path)
    in_file = open(in_path, 'rb')
    out_file = open(out_path, 'wb')

    PrintMetadata(in_file, out_file)

    out_file.write(in_file.read())

    out_file.close()
    in_file.close()

def Main():
  parser = argparse.ArgumentParser(description='Process traces')
  parser.add_argument('output_path', help='Output path')
  parser.add_argument('--local_path', help='Import files from local path')
  args = parser.parse_args()

  print 'import_path: %s' % str(args.local_path)

  output_path = os.path.abspath(args.output_path)
  print 'Output path: %s' % output_path

  if args.local_path != None:
    ImportFromLocalFolder(os.path.abspath(args.local_path), output_path)

if __name__ == '__main__':
  Main()
