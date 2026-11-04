"""Rastrillo V01 - concepto editable mediante parametros. Unidades: mm.
Ejecutar con CadQuery 2.8. No es un diseno liberado para fabricar molde.
"""
from pathlib import Path
import sys, math, json
HERE=Path(__file__).resolve().parent
if (HERE/'_deps').exists(): sys.path.insert(0,str(HERE/'_deps'))
import cadquery as cq
from cadquery import Vector as V

OUT=HERE/'entrega'
OUT.mkdir(exist_ok=True)
N=26
PANEL=2.8
TINE=3.0
WIDTH=8.0
RIB=1.5
ORIGIN_Y=35.0
BEND_R=20.0
BEND_A=math.radians(70)
TIP=16.0

def local_to_head(s,a):
    return s.rotate((0,0,0),(0,0,1),-math.degrees(a)).translate((0,ORIGIN_Y,0))

def rib(s0,s1,h0,h1,a):
    # Section in YZ; 0.3 mm overlap with the supporting wall.
    pts=[V(-RIB/2,s0,.3),V(-RIB/2,s1,.3),V(-RIB/2,s1,-h1),V(-RIB/2,s0,-h0)]
    w=cq.Wire.makePolygon(pts+[pts[0]])
    return local_to_head(cq.Solid.extrudeLinear(w,[],V(RIB,0,0)),a)

def tooth(rad,a):
    # Exact circular bend, 3 mm section thickness; extrusion gives an 8 mm tooth.
    b=rad-BEND_R*math.sin(BEND_A)-TIP*math.cos(BEND_A)
    x=-WIDTH/2
    def pt(y,z):return V(x,y,z)
    def arcpt(r,ang):return pt(b+r*math.sin(ang),-BEND_R+r*math.cos(ang))
    r1=BEND_R+TINE/2; r2=BEND_R-TINE/2
    start1=pt(162,TINE/2); tangent1=pt(b,TINE/2)
    end1=arcpt(r1,BEND_A); tip1=end1+V(0,TIP*math.cos(BEND_A),-TIP*math.sin(BEND_A))
    end2=arcpt(r2,BEND_A); tip2=end2+V(0,TIP*math.cos(BEND_A),-TIP*math.sin(BEND_A))
    tangent2=pt(b,-TINE/2); start2=pt(162,-TINE/2)
    edges=[cq.Edge.makeLine(start1,tangent1),cq.Edge.makeThreePointArc(tangent1,arcpt(r1,BEND_A/2),end1),cq.Edge.makeLine(end1,tip1),cq.Edge.makeLine(tip1,tip2),cq.Edge.makeLine(tip2,end2),cq.Edge.makeThreePointArc(end2,arcpt(r2,BEND_A/2),tangent2),cq.Edge.makeLine(tangent2,start2),cq.Edge.makeLine(start2,start1)]
    s=cq.Solid.extrudeLinear(cq.Wire.assembleEdges(edges),[],V(WIDTH,0,0))
    # Ease exposed perimeter to eliminate knife edges on the conceptual tooth.
    try:s=s.fillet(.6,[e for e in s.Edges() if abs(e.Length()-WIDTH)<.01 and e.Center().y>b+10])
    except Exception:pass
    return local_to_head(s,a)

def main():
    print('Building 26 curved teeth',flush=True)
    # Centers adjusted so the nominal envelope is approximately 600 x 430.
    xs=[-296.05+592.10*i/(N-1) for i in range(N)]
    ends=[];teeth=[]
    for x in xs:
        y=428.57-65*(x/296.05)**2
        a=math.atan2(x,y-ORIGIN_Y);r=math.hypot(x,y-ORIGIN_Y)
        ends.append((a,r));teeth.append(tooth(r,a))
    amax=abs(ends[0][0])
    # Smooth fan panel with curved lower boundary.
    rim=[(170*math.sin(a),ORIGIN_Y+170*math.cos(a)) for a in [amax-2*amax*i/24 for i in range(25)]]
    rv=[V(x,y,0) for x,y in rim]
    pw=cq.Wire.assembleEdges([cq.Edge.makeLine(V(-13,18,0),V(13,18,0)),cq.Edge.makeLine(V(13,18,0),rv[0]),cq.Edge.makeSpline(rv),cq.Edge.makeLine(rv[-1],V(-13,18,0))])
    panel=cq.Solid.extrudeLinear(pw,[],V(0,0,PANEL))
    # Curved 9 mm bridge follows the radial tooth distribution.
    outer=[((.77*r+4.5)*math.sin(a),ORIGIN_Y+(.77*r+4.5)*math.cos(a)) for a,r in ends]
    inner=[((.77*r-4.5)*math.sin(a),ORIGIN_Y+(.77*r-4.5)*math.cos(a)) for a,r in reversed(ends)]
    ov=[V(x,y,-1.5) for x,y in outer];iv=[V(x,y,-1.5) for x,y in inner]
    bw=cq.Wire.assembleEdges([cq.Edge.makeSpline(ov),cq.Edge.makeLine(ov[-1],iv[0]),cq.Edge.makeSpline(iv),cq.Edge.makeLine(iv[-1],ov[0])])
    bridge=cq.Solid.extrudeLinear(bw,[],V(0,0,4.5))
    outer_socket=cq.Solid.makeCylinder(15.7,96,V(0,0,14),V(0,1,0))
    ribs=[rib(164,.77*r,5.5,1.0,a) for a,r in ends]
    ribs += [rib(40,169,10,5.5,a) for a in [-amax,-amax/2,0,amax/2,amax]]
    # Two neck gussets, connecting outer socket to panel.
    for sign in [-1,1]:
        pts=[V(sign*12,22,2),V(sign*12,80,23),V(sign*65,144,2)]
        w=cq.Wire.makePolygon(pts+[pts[0]])
        ribs.append(cq.Solid.extrudeLinear(w,[],V(sign*1.5,0,0)))
    parts=[panel,bridge,outer_socket]+teeth+ribs
    print('Fusing connected features',flush=True)
    head=parts[0].fuse(*parts[1:]).clean()
    # Blind socket: 25.4 nominal diameter, 90 insertion, 6 mm end cap.
    bore=cq.Solid.makeCylinder(12.7,90.1,V(0,-.1,14),V(0,1,0))
    # Radial pilot clearance through upper socket wall only.
    screw=cq.Solid.makeCylinder(2.25,12,V(0,35,24),V(0,0,1))
    head=head.cut(bore).cut(screw).clean()
    assert head.isValid(),'Invalid boundary representation'
    assert len(head.Solids())==1,f'Expected one solid, got {len(head.Solids())}'
    print('Exporting STEP',flush=True)
    head.exportStep(str(OUT/'Rastrillo_V01.step'))
    head.exportStl(str(OUT/'Rastrillo_V01.stl'),tolerance=.15,angularTolerance=.15)
    from OCP.STEPControl import STEPControl_Reader
    reader=STEPControl_Reader()
    reader.ReadFile(str(OUT/'Rastrillo_V01.step'))
    reader.TransferRoots()
    reread=cq.Shape.cast(reader.OneShape())
    assert reread.isValid() and len(reread.Solids())==1
    assert abs(reread.Volume()-head.Volume())/head.Volume()<1e-6
    bb=head.BoundingBox()
    report={'valid_brep':head.isValid(),'solids':len(head.Solids()),'teeth':N,'units':'mm','bbox_mm':[bb.xlen,bb.ylen,bb.zlen],'volume_mm3':head.Volume(),'estimated_mass_g_at_0.90_g_cm3':head.Volume()*.0009,'step_roundtrip_valid':True,'panel_mm':PANEL,'tooth_section_mm':[WIDTH,TINE],'rib_thickness_mm':RIB,'socket_diameter_mm':25.4,'socket_depth_mm':90,'bend_center_radius_mm':20,'bend_angle_deg':70,'tip_straight_length_mm':16,'fixing_hole_mm':4.5,'status':'Concepto para revision; sin validacion de molde, material, esfuerzos o fatiga.'}
    (OUT/'Verificacion_V01.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report),flush=True)
    # Preview geometry is tessellated from this verified solid, never image-generated.
    vs,ts=head.tessellate(.35,.2)
    import numpy as np
    np.savez_compressed(OUT/'malla_preview.npz',vertices=np.array([v.toTuple() for v in vs]),triangles=np.array(ts))

if __name__=='__main__':main()
