import re
import sys
import json
from pathlib import Path
class HTMLparser:
 def __init__(self, infilename, outfilename, contextfilename, *args):
  string =  r'/\*\*\s*(include'
  if args == ():
   for i in ("variable","loopover","endloop","loopvar"):
    string += f"|{i}"
   string += ")"
  else:
   for i in args:
    string += f"|{i}"
   string += ")"
  self.DIRECTIVE_RE=re.compile(
   f"{string}"
   r'\s*([^ *]*)\s*\*\*/'
   )
  self.template = open(infilename).read()
  self.working_dir = Path(infilename).absolute().parent
  self.pos = 0
  self.outfile = open(outfilename, 'w')
  with open(contextfilename) as contextfile:
   self.context = json.load(contextfile)
   
 def process(self):
  print("prossesing...")
  match = self.DIRECTIVE_RE.search(self.template, pos=self.pos)
  while match:
   self.outfile.write(self.template[self.pos:match.start()])
   directive, argument = match.groups()
   method_name = 'process_{}'.format(directive)
   getattr(self, method_name)(match, argument)
   match = self.DIRECTIVE_RE.search(self.template, pos=self.pos)
  print(self.template[self.pos:])
  self.outfile.write(self.template[self.pos:])
  print("done")
 def process_include(self, match, argument):
  with (self.working_dir / argument).open() as includefile:
   self.outfile.write(includefile.read())
   self.pos = match.end()
  
 def process_variable(self, match, argument):
  self.outfile.write(self.context.get(argument, ''))
  self.pos = match.end()
  
 def process_loopover(self, match, argument):
  self.loop_index = 0
  self.loop_list = self.context.get(argument, [])
  self.pos = self.loop_pos = match.end()
 
 def process_loopvar(self, match, argument):
  self.outfile.write(self.loop_list[self.loop_index])
  self.pos = match.end()

 def process_endloop(self, match, argument):
   self.loop_index += 1
   if self.loop_index >= len(self.loop_list):
    self.pos = match.end()
    del self.loop_index
    del self.loop_list
    del self.loop_pos
   else:
    self.pos = self.loop_pos

