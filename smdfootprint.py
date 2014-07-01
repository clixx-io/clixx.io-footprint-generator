# /usr/bin/python

# creates a .fzp file in ~/.config/Fritzing/parts/user

import argparse
import ConfigParser
import svgwrite
from svgwrite.container import Group
from svgwrite.mixins import Transform

class smd:
    configuration_file = "footprints.ini"
	
    def __init__(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read(self.configuration_file)
	
    def load_footprint(self,footprint_name):
		"""
		Returns all configuration keys for a particular SMD 
		footprint from the configuration in a dictionary
		"""
		if footprint_name not in self.config.sections():
			print "Error: That footprint doesn't exist in %s" % self.configuration_file
			return None
			
		footprint_info = {}
		for option in self.config.options(footprint_name):
			print " ", option, "=", self.config.get(footprint_name, option)
			footprint_info[option] = self.config.get(footprint_name, option)

		return footprint_info
			
    def generate_pcb(self, footprint_name, specs):

        total_pincount     = eval(specs['total_pincount'])
        pad_pitch          = eval(specs['pad_pitch'])
        pad_width          = eval(specs['pad_width'])
        pad_length         = eval(specs['pad_length'])
        lead_to_lead_length= eval(specs['lead_to_lead_length'])
        if specs.has_key('sides'):
		    sides          = eval(specs['sides'])
        else:
			sides          = 2
        if specs.has_key('top_margin'):
			top_margin     = eval(specs['top_margin'])
        else:
			top_margin	   = 1	
        if specs.has_key('left_margin'):
            left_margin    = eval(specs['left_margin'])
        else:
            left_margin    = 1
        if specs.has_key('ic_label'):
			ic_label       = eval(specs['ic_label'])
        else:
		    ic_label       = 'IC'

        footprint_width    = str((2 * left_margin) + (pad_pitch * (total_pincount / sides)))
        footprint_height   = str((2 * top_margin) + (pad_length * 2) + lead_to_lead_length)

        # Create the document        
        svg_document = svgwrite.Drawing(filename = footprint_name + ".svg",size=(footprint_width+'mm', footprint_height+'mm'), 
                                        viewBox=('0 0 ' + str(footprint_width) + ' ' + str(footprint_height)))

        # Create the silkscreen
        silkscreen = Group(id='Silkscreen')
        if sides==2:
			# x
            line_1     = left_margin - pad_width
            line_2     = left_margin + ((total_pincount / sides) * pad_pitch) 
			# y
            line_start = top_margin + (pad_length / 2)
            line_end   = top_margin + lead_to_lead_length + + (pad_length / 2)
            silkscreen.add(svg_document.line(start=(line_1, line_start), end=(line_1,line_end),
                                               stroke_width = pad_width,
                                               stroke = "white",
                                               fill = "rgb(255,255,255)"))
            silkscreen.add(svg_document.line(start=(line_2, line_start), end=(line_2,line_end),
                                               stroke_width = pad_width,
                                               stroke = "white",
                                               fill = "rgb(255,255,255)"))
			
            # silkscreen.add(svg_document.text(ic_label,insert = (30, 30)))
        svg_document.add(silkscreen)

        copper_layer = Group(id='copper1')
        if sides >= 1:
            for s in range(0,sides):

                if s==0:
                    side_start = top_margin
                elif s==1:
                    side_start = top_margin + lead_to_lead_length
            
                for p in range(0,total_pincount / sides):

                    # svg_document.add(svg_document.translate((s, 40)))

                    copper_layer.add(svg_document.rect(insert = (left_margin + (p * pad_pitch), side_start),
                                       size = (pad_width, pad_length),
                                       stroke_width = "0",
                                       stroke = "black",
                                       fill = "rgb(0,0,0)"))
       
        svg_document.add(copper_layer)
        
        # print(svg_document.tostring())

        svg_document.save()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate SMD Footprints for Fritzing.',
									 epilog="Consult hackerpads.com for more information")

    parser.add_argument('-f', action="store", dest="f")

    ic = smd()

    try:
        results = parser.parse_args()
        print 'Generating for footprint %s' % results.f
        specs = ic.load_footprint(results.f)
        if specs is None:
			print "SMD Information not found"
        else:	
            ic.generate_pcb(results.f, specs)
			
    except IOError, msg:
        parser.error(str(msg))
   
