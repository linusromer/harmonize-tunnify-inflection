#!/usr/bin/env python

#harmonize_tunnify_inflection version 20191124

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.

#Copyright 2019 by Linus Romer
"""
harmonize_tunnify_inflection.py is a FontForge plug-in to 
harmonize or tunnify or add inflection points to the selected parts.
Installation: FontForge says that you have to copy the file to 
$(PREFIX)/share/fontforge/python or ~/.FontForge/python
but for me (on Linux) it works at
~/.config/fontforge/python
and for Windows it might be at
C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python
You then will find "Harmonize" and "Tunnify" in the "Tools" menu.
"""

import fontforge,psMat,math

# Returns the euclidean distance between point a = (ax,ay) 
# and b = (bx,by).
def distance(ax,ay,bx,by):
	return ((ax-bx)**2+(ay-by)**2)**.5
	
# Returns 1 iff the point p is to the right of the line
# going from point q through point r,
# returns -1 iff the point p is to the left of the line,
# returns 0 iff the point p is to the left of the line
def side(px,py,qx,qy,rx,ry):
	crossproduct = (rx-qx)*(qy-py) - (ry-qy)*(qx-px)
	if crossproduct > 0:
		return 1
	elif crossproduct < 0:
		return -1	
	else:
		return 0	
		
# Checks if a = (ax,ay) and b = (bx,by) and c = (cx,cy) are approx. on
# one line where b is supposed to be inbetween.
def on_same_line(ax,ay,bx,by,cx,cy):
	return abs(math.atan2(by-ay,bx-ax)-math.atan2(cy-by,cx-bx))<.05

# Splits a contour c after point number i and time 0 < t < 1
# such that the bezier segment c[i],c[i+1],c[i+2],c[i+3]
# becomes two segments c[i],q1,q2,q3 and
# q3,r1,r2,c[i+3].
def split(c,i,t):
	l = len(c)
	if 0 < t < 1 and i % 1 == 0 and 0 <= i < l and c[i].on_curve \
	and not c[i+1].on_curve and not c[i+2].on_curve \
	and c[(i+3)%l].on_curve:
		qx1 = c[i].x + t*(c[i+1].x-c[i].x)
		qy1 = c[i].y + t*(c[i+1].y-c[i].y)
		qx2 = c[i+1].x + t*(c[i+2].x-c[i+1].x)
		qy2 = c[i+1].y + t*(c[i+2].y-c[i+1].y)
		rx2 = c[i+2].x + t*(c[(i+3)%l].x-c[i+2].x)
		ry2 = c[i+2].y + t*(c[(i+3)%l].y-c[i+2].y)
		rx1 = qx2 + t*(rx2-qx2)
		ry1 = qy2 + t*(ry2-qy2)
		qx2 = qx1 + t*(qx2-qx1)
		qy2 = qy1 + t*(qy2-qy1)
		qx3 = qx2 + t*(rx1-qx2)
		qy3 = qy2 + t*(ry1-qy2)     
		doublesegment = fontforge.contour()
		doublesegment.moveTo(c[i].x,c[i].y)
		doublesegment.cubicTo(qx1,qy1,qx2,qy2,qx3,qy3)
		doublesegment.cubicTo(rx1,ry1,rx2,ry2,c[(i+3)%l].x,c[(i+3)%l].y)
		if i+3 == l and c.closed: # end point is starting point 
			c.makeFirst(i)
			c[0:4] = doublesegment
			c.makeFirst(l+3-i)
		else: # generic case
			c[i:i+4] = doublesegment
		
# Returns the corner point c which is the intersection of the
# lines a1--a2 and b1--b2 or None if there is no intersection.
def corner_point(a1x,a1y,a2x,a2y,b1x,b1y,b2x,b2y):
	if ((a1x*b1y)-(a1x*b2y)-(a1y*b1x)+(a1y*b2x)
	-(a2x*b1y)+(a2x*b2y)+(a2y*b1x)-(a2y*b2x)) == 0 \
	and ((a1x*b1y)-(a1x*b2y)-(a1y*b1x)+(a1y*b2x) \
	-(a2x*b1y)+(a2x*b2y)+(a2y*b1x)-(a2y*b2x)) == 0:
		return None
	else:
		return ((((-a1x)+a2x)*((a1x*b1y)-(a1x*b2y)-(a1y*b1x)+(a1y*b2x)
		+(b1x*b2y)-(b1y*b2x))/((a1x*b1y)-(a1x*b2y)-(a1y*b1x)+(a1y*b2x)
		-(a2x*b1y)+(a2x*b2y)+(a2y*b1x)-(a2y*b2x)))+a1x ,
		(((-a1y)+a2y)*((a1x*b1y)-(a1x*b2y)-(a1y*b1x)+(a1y*b2x)
		+(b1x*b2y)-(b1y*b2x))/((a1x*b1y)-(a1x*b2y)-(a1y*b1x)+(a1y*b2x)
		-(a2x*b1y)+(a2x*b2y)+(a2y*b1x)-(a2y*b2x)))+a1y)
		
# Returns the inflection time of a cubic bezier segment
# (a,b),(c,d),(e,f),(g,h).
# If there is no inflection point, None is returned.
def inflection(a,b,c,d,e,f,g,h):
	# curvature=0 is an equation aa*t**2+bb*t+c=0 with coefficients: 
	aa = e*h-2*c*h+a*h-f*g+2*d*g-b*g+3*c*f-2*a*f-3*d*e+2*b*e+a*d-b*c
	bb = c*h-a*h-d*g+b*g-3*c*f+3*a*f+3*d*e-3*b*e-2*a*d+2*b*c
	cc = c*f-a*f-d*e+b*e+a*d-b*c
	if aa == 0 and not bb == 0 and 0.001 < -c/bb < 0.999: # linear eq.
		return -c/bb
	else:
		discriminant = bb**2-4*aa*cc
		if discriminant >= 0 and not aa == 0:
			t1 = (-bb + discriminant**.5)/(2*aa)
			t2 = (-bb - discriminant**.5)/(2*aa)
			if 0.001 < t1 < 0.999: # rounding issues
				return t1
			elif 0.001 < t2 < 0.999:
				return t2
	return None
			
# Adds missing inflection points to a fontforge contour c.
# The boolean is_glyph_variant is true iff
# we do not care whether the points are selected in the UI.
def inflection_contour(c,is_glyph_variant):
	l = len(c)
	j = 0 # index that will run from 0 to l-1 (may contain jumps)
	while j < l: # going through the points c[j]
		# if a point is selected
		# search for the next on_curve point
		# this must be the overovernext point
		# (which is the only case
		# that interests us)
		if (c[j].selected or is_glyph_variant) \
		and not c[(j+1)%l].on_curve \
		and not c[(j+2)%l].on_curve \
		and c[(j+3)%l].on_curve \
		and (c[(j+3)%l].selected or is_glyph_variant) \
		and (j+3)%l != j:
			t = inflection(c[j].x,c[j].y,c[(j+1)%l].x,c[(j+1)%l].y,
			c[(j+2)%l].x,c[(j+2)%l].y,c[(j+3)%l].x,c[(j+3)%l].y)
			if not t is None:
				split(c,j,t)
				if not is_glyph_variant:
					c[(j+3)%l].selected = True # mark new points
				j += 3 # we just added 3 points...
				l += 3 # we just added 3 points...
			j += 2 # we can jump by 2+1 instead of 1
		j += 1

# Tunnifies a cubic bezier path a0,a1,a2,a3
# i.e. moves the handles a1 and a2 on the lines a0--a1 and a2--a3 resp.
# in order to fulfill the tunni ideal stated by Eduardo Tunni.
def tunnify(a0x,a0y,a1x,a1y,a2x,a2y,a3x,a3y):
	# check if the handles are on the same side 
	# and no inflection occurs:
	if side(a1x,a1y,a0x,a0y,a3x,a3y)*side(a2x,a2y,a0x,a0y,a3x,a3y) > 0 \
	and inflection(a0x,a0y,a1x,a1y,a2x,a2y,a3x,a3y) is None:
		c = corner_point(a0x,a0y,a1x,a1y,a2x,a2y,a3x,a3y)
		if not c is None:
			cx,cy = c
			d1 = distance(cx,cy,a0x,a0y)
			d2 = distance(cx,cy,a3x,a3y)
			if not d1 == 0 and not d2 == 0:
				t1 = distance(a1x,a1y,a0x,a0y)/d1
				t2 = distance(a2x,a2y,a3x,a3y)/d2
				t = .5*(t1+t2)
				return (1-t)*a0x+t*cx,(1-t)*a0y+t*cy,(1-t)*a3x+t*cx,(1-t)*a3y+t*cy
	return a1x,a1y,a2x,a2y	
		
# Tunnifies the handles of a fontforge contour c.
# The boolean is_glyph_variant is true iff
# we do not care whether the points are selected in the UI.
def tunnify_contour(c,is_glyph_variant):
	l = len(c)
	j = 0 # index that will run from 0 to l-1 (may contain jumps)
	while j < l: # going through the points c[j]
		# if a point is selected
		# search for the next on_curve point
		# this must be the overovernext point
		# (which is the only case
		# that interests us)
		if (c[j].selected or is_glyph_variant) \
		and not c[(j+1)%l].on_curve \
		and not c[(j+2)%l].on_curve \
		and c[(j+3)%l].on_curve \
		and (c[(j+3)%l].selected or is_glyph_variant) \
		and (j+3)%l != j:
			c[(j+1)%l].x,c[(j+1)%l].y,c[(j+2)%l].x,c[(j+2)%l].y = \
			tunnify(c[j].x, c[j].y,	c[(j+1)%l].x, c[(j+1)%l].y, 
			c[(j+2)%l].x, c[(j+2)%l].y, c[(j+3)%l].x, c[(j+3)%l].y)
			j += 2 # we can jump by 2+1 instead of 1
		j += 1
			
# This is the harmonize algorithm as described at
# https://gist.github.com/simoncozens/3c5d304ae2c14894393c6284df91be5b
# by Simon Cozens. This is the variant, where the nodes may move
# but not the handles (in the following called harmonize in opposition
# to harmonize_handles).
# Given two successive cubic bezier curves a0,a1,a2,a3 and b0,b1,b2,b3 
# that are smooth at a3 = b0 (i.e. a2, a3 = b0 and b1 are on one line)
# we calculate the corner point c which is the intersection of the
# lines a1--a2 and b1--b2.
# Determine the ratios pa = |a1, a2| / |a2, d| 
# and pb = |d1, b1| / |b1, b2|.
# Calculate the ratio p = (p0 * p1) ** .5
# Place a3 = b0 such that it is situated at t = p / (p+1) 
# of the line a2--b1.
def harmonize(a1x,a1y,a2x,a2y,a3x,a3y,b1x,b1y,b2x,b2y):
	c = corner_point(a1x,a1y,a2x,a2y,b1x,b1y,b2x,b2y)
	if not c is None:
		cx,cy = c
		if not distance(cx,cy,a2x,a2y) == 0 \
		and not distance(b1x,b1y,b2x,b2y) == 0:
			pa = distance(a1x,a1y,a2x,a2y)/distance(cx,cy,a2x,a2y)
			pb = distance(cx,cy,b1x,b1y)/distance(b1x,b1y,b2x,b2y)
			p = (pa*pb)**.5
			return (a2x+p/(p+1)*(b1x-a2x),a2y+p/(p+1)*(b1y-a2y))
		else:
			return (a3x,a3y)
	else:
		return (a3x,a3y)

# Harmonizes the nodes of a fontforge contour c.
# The boolean is_glyph_variant is true iff
# we do not care whether the points are selected in the UI.
# The boolean is_handles_variant is true iff
# we use harmonize_handles() instead of harmonize().
def harmonize_contour(c,is_glyph_variant,is_handles_variant):
	l = len(c)
	j = 0 # index that will run from 0 to l-1 (may contain jumps)
	while j < l: # going through the points c[j]
		# if a point is selected
		# search for the next on_curve point
		# this must be the overovernext point
		# (which is the only case
		# that interests us) and so on...
		if (c[j].selected or is_glyph_variant) \
		and not c[(j+1)%l].on_curve \
		and not c[(j+2)%l].on_curve \
		and c[(j+3)%l].on_curve \
		and (c[(j+3)%l].selected or is_glyph_variant) \
		and (j+3)%l != j \
		and not c[(j+4)%l].on_curve \
		and not c[(j+5)%l].on_curve \
		and c[(j+6)%l].on_curve \
		and (c[(j+6)%l].selected or is_glyph_variant) \
		and (j+6)%l != j \
		and on_same_line(c[(j+2)%l].x,c[(j+2)%l].y, \
		c[(j+3)%l].x,c[(j+3)%l].y,c[(j+4)%l].x,c[(j+4)%l].y):
			ideal = harmonize(c[(j+1)%l].x, c[(j+1)%l].y, 
			c[(j+2)%l].x, c[(j+2)%l].y, 
			c[(j+3)%l].x, c[(j+3)%l].y, 
			c[(j+4)%l].x, c[(j+4)%l].y, 
			c[(j+5)%l].x, c[(j+5)%l].y)
			deltax,deltay = ideal[0]-c[(j+3)%l].x,ideal[1]-c[(j+3)%l].y
			if is_handles_variant:
				c[(j+2)%l].transform(psMat.translate(-deltax,-deltay))
				c[(j+4)%l].transform(psMat.translate(-deltax,-deltay))
			else:
				c[(j+3)%l].transform(psMat.translate(deltax,deltay))
			j += 3
		else:
			j += 1

# Harmonizes or tunnifies or adds inflection points
# to the selected contours (for glyph view).
# The string action is either "harmonize", "harmonize_handles",
# "tunnify" or "inflection".
def modify_contours(action,glyph):
	glyph.preserveLayerAsUndo()
	layer = glyph.layers[glyph.activeLayer]
	# first, we check, if anything is selected at all
	# because nothing selected means that the whole glyph
	# should be harmonized (at least the author thinks so)
	is_glyph_variant = True # temporary
	for i in range(len(layer)): # going through the contours layer[i]
		for j in range(len(layer[i])):
			if layer[i][j].selected:
				is_glyph_variant = False
				break
	for i in range(len(layer)): # going through the contours layer[i]
		if action == "harmonize":
			harmonize_contour(layer[i],is_glyph_variant,False)
		elif action == "harmonize_handles":
			harmonize_contour(layer[i],is_glyph_variant,True)
		elif action == "tunnify":
			tunnify_contour(layer[i],is_glyph_variant)
		elif action == "inflection":
			inflection_contour(layer[i],is_glyph_variant)
	glyph.layers[glyph.activeLayer] = layer
	
# Harmonizes or tunnifies or adds inflection points
# to the selected glyphs (for font view).
# The string action is either "harmonize", "harmonize_handles",
# "tunnify" or "inflection".
def modify_glyphs(action,font):
	for glyph in font.selection.byGlyphs:
		glyph.preserveLayerAsUndo()
		layer = glyph.layers[glyph.activeLayer]
		for i in range(len(layer)):
			if action == "harmonize":
				harmonize_contour(layer[i],True,False)
			elif action == "harmonize_handles":
				harmonize_contour(layer[i],True,True)
			elif action == "tunnify":
				tunnify_contour(layer[i],True)
			elif action == "inflection":
				inflection_contour(layer[i],True)
		glyph.layers[glyph.activeLayer] = layer
		
# Returns false iff no glyph is selected 
# (needed for enabling in tools menu).
def are_glyphs_selected(junk,font):
	font = fontforge.activeFont()
	for glyph in font.selection.byGlyphs:
		return True
	return False

# Returns always True (needed for enabling in tools menu).
def are_contours_selected(junk,font):
	return True

# Registers the tools in the tools menu of FontForge.
if fontforge.hasUserInterface():
	fontforge.registerMenuItem(modify_glyphs,are_glyphs_selected,"harmonize","Font",None,"Harmonize");
	fontforge.registerMenuItem(modify_glyphs,are_glyphs_selected,"harmonize_handles","Font",None,"Harmonize handles");
	fontforge.registerMenuItem(modify_glyphs,are_glyphs_selected,"tunnify","Font",None,"Tunnify (balance)");
	fontforge.registerMenuItem(modify_glyphs,are_glyphs_selected,"inflection","Font",None,"Add points of inflection");
	fontforge.registerMenuItem(modify_contours,are_contours_selected,"harmonize","Glyph",None,"Harmonize");
	fontforge.registerMenuItem(modify_contours,are_contours_selected,"harmonize_handles","Glyph",None,"Harmonize handles");
	fontforge.registerMenuItem(modify_contours,are_contours_selected,"tunnify","Glyph",None,"Tunnify (balance)");
	fontforge.registerMenuItem(modify_contours,are_contours_selected,"inflection","Glyph",None,"Add points of inflection");
