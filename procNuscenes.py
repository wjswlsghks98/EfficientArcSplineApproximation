import os
import lanelet2
from lanelet2.core import (Lanelet, LaneletMap)
from lanelet2.projection import (LocalCartesianProjector)
import lanelet2.traffic_rules
import scipy.io as sio

class procNuScenes :
    def __init__(self,file_path,org):
        self.projector = LocalCartesianProjector(lanelet2.io.Origin(org[0], org[1]))
        self.path = file_path
        self.map = lanelet2.io.load(self.path,self.projector)
    def process(self):
        traffic_rules = lanelet2.traffic_rules.create(lanelet2.traffic_rules.Locations.Germany,
                                                      lanelet2.traffic_rules.Participants.Vehicle)
        graph = lanelet2.routing.RoutingGraph(self.map, traffic_rules)
        edges = []
        llt_id_lst = []
        ls_pts = []
        ls_ids = []
        ls_frontNode_ids = []
        ls_backNode_ids = []

        # Traverse through all lanelets in the map
        for llt in self.map.laneletLayer:
            llt_id_lst.append(llt.id)
            abs_curr_leftBound_id = abs(llt.leftBound.id)
            abs_curr_rightBound_id = abs(llt.rightBound.id)
            if llt.leftBound.inverted():
                left = [[p.x, p.y, p.z] for p in llt.leftBound.invert()]
                curr_leftBound_id = abs_curr_leftBound_id * -1
                left_frontNode_id = llt.leftBound[-1].id
                left_backNode_id = llt.leftBound[0].id
            else:
                left = [[p.x, p.y, p.z] for p in llt.leftBound]
                curr_leftBound_id = abs_curr_leftBound_id
                left_frontNode_id = llt.leftBound[0].id
                left_backNode_id = llt.leftBound[-1].id

            if llt.rightBound.inverted():
                right = [[p.x, p.y, p.z] for p in llt.rightBound.invert()]
                curr_rightBound_id = abs_curr_rightBound_id * -1
                right_frontNode_id = llt.rightBound[-1].id
                right_backNode_id = llt.rightBound[0].id
            else:
                right = [[p.x, p.y, p.z] for p in llt.rightBound]
                curr_rightBound_id = abs_curr_rightBound_id
                right_frontNode_id = llt.rightBound[0].id
                right_backNode_id = llt.rightBound[-1].id

            # Only append non-overlapping linestring information
            if not (abs_curr_leftBound_id in ls_ids):
                ls_ids.append(abs_curr_leftBound_id)
                ls_pts.append(left)
                ls_frontNode_ids.append(left_frontNode_id)
                ls_backNode_ids.append(left_backNode_id)

            if not (abs_curr_rightBound_id in ls_ids):
                ls_ids.append(abs_curr_rightBound_id)
                ls_pts.append(right)
                ls_frontNode_ids.append(right_frontNode_id)
                ls_backNode_ids.append(right_backNode_id)

            
            print("Current Lanelet ID: ",llt.id)
            print("==================================")
            next_llts = graph.following(llt)

            for next_llt in next_llts:
                print("Next Lanelet ID: ",next_llt.id)
                print("Next Lanelet Left Linestring ID: ",next_llt.leftBound.id)
                print("Next Lanelet Right Linestring ID: ",next_llt.rightBound.id)
                print("Next Lanelet Left Linestring Inverted?: ",next_llt.leftBound.inverted())
                print("Next Lanelet Right Linestring Inverted?: ",next_llt.rightBound.inverted())
                
                
                abs_next_leftBound_id = abs(next_llt.leftBound.id)
                abs_next_rightBound_id = abs(next_llt.rightBound.id)
                
                if next_llt.leftBound.inverted():
                    # print("Not inverted point ids: ",self.map.lineStringLayer[next_llt.leftBound.id])
                    # print("First point ID: ",self.map.lineStringLayer[next_llt.leftBound.id][0].id)
                    # print("Last point ID: ",self.map.lineStringLayer[next_llt.leftBound.id][-1].id)
                    # print("Linestring saved in next lanelet: ",next_llt.leftBound)
                    # print("First point ID: ",next_llt.leftBound[0].id)
                    # print("Last point ID: ",next_llt.leftBound[-1].id)

                    next_leftBound_id = abs_next_leftBound_id * -1
                    next_left = [[p.x, p.y, p.z] for p in next_llt.leftBound.invert()]
                    next_left_frontNode_id = next_llt.leftBound[-1].id
                    next_left_backNode_id = next_llt.leftBound[0].id
                else:
                    next_leftBound_id = abs_next_leftBound_id
                    next_left = [[p.x, p.y, p.z] for p in next_llt.leftBound]
                    next_left_frontNode_id = next_llt.leftBound[0].id
                    next_left_backNode_id = next_llt.leftBound[-1].id
                    
                if next_llt.rightBound.inverted():
                    next_rightBound_id = abs_next_rightBound_id * -1
                    next_right = [[p.x, p.y, p.z] for p in next_llt.rightBound.invert()]
                    next_right_frontNode_id = next_llt.rightBound[-1].id
                    next_right_backNode_id = next_llt.rightBound[0].id
                else:
                    next_rightBound_id = abs_next_rightBound_id
                    next_right = [[p.x, p.y, p.z] for p in next_llt.rightBound]
                    next_right_frontNode_id = next_llt.rightBound[0].id
                    next_right_backNode_id = next_llt.rightBound[-1].id

                # Add non-overlapping linestrings
                if not (abs_next_leftBound_id in ls_ids):
                    ls_ids.append(abs_next_leftBound_id)
                    ls_pts.append(next_left)
                    ls_frontNode_ids.append(next_left_frontNode_id)
                    ls_backNode_ids.append(next_left_backNode_id)
                
                if not (abs_next_rightBound_id in ls_ids):
                    ls_ids.append(abs_next_rightBound_id)
                    ls_pts.append(next_right)
                    ls_frontNode_ids.append(next_right_frontNode_id)
                    ls_backNode_ids.append(next_right_backNode_id)

                # Remove repeated or equivalent edges
                if not ((curr_leftBound_id, next_leftBound_id) in edges or (-next_leftBound_id, -curr_leftBound_id) in edges):
                    edges.append((curr_leftBound_id, next_leftBound_id))
                
                if not ((curr_rightBound_id, next_rightBound_id) in edges or (-next_rightBound_id, -curr_rightBound_id) in edges):
                    edges.append((curr_rightBound_id, next_rightBound_id))
                
                # Verify connection!
                # 1. Left Boundaries
                if curr_leftBound_id > 0 and next_leftBound_id > 0:
                    assert left_backNode_id == next_left_frontNode_id, "Left, Case 1 Match Failure."
                elif curr_leftBound_id > 0 and next_leftBound_id < 0:
                    assert left_backNode_id == next_left_backNode_id, "Left Case 2 Match Failure."
                elif curr_leftBound_id < 0 and next_leftBound_id > 0:
                    assert left_frontNode_id == next_left_frontNode_id, "Left Case 3 Match Failure."
                elif curr_leftBound_id < 0 and next_leftBound_id < 0:
                    assert left_frontNode_id == next_left_backNode_id, "Left Case 4 Match Failure."    
                
                # 2. Right Boundaries
                if curr_rightBound_id > 0 and next_rightBound_id > 0:
                    assert right_backNode_id == next_right_frontNode_id, "Right, Case 1 Match Failure."
                elif curr_rightBound_id > 0 and next_rightBound_id < 0:
                    assert right_backNode_id == next_right_backNode_id, "Right Case 2 Match Failure."
                elif curr_rightBound_id < 0 and next_rightBound_id > 0:
                    assert right_frontNode_id == next_right_frontNode_id, "Right Case 3 Match Failure."
                elif curr_rightBound_id < 0 and next_rightBound_id < 0:
                    assert right_frontNode_id == next_right_backNode_id, "Right Case 4 Match Failure."

                print("----------------------------------")
            print("==================================")
        
        # Save
        path_lst_ids = self.path.split("/")
        path_lst_pts = self.path.split("/")
        path_lst_edges = self.path.split("/")
        path_lst_frontNodeIds = self.path.split("/")
        path_lst_backNodeIds = self.path.split("/")

        last_el_ids = path_lst_ids[-1][0:-4] + "-ids.mat"
        last_el_pts = path_lst_pts[-1][0:-4] + "-pts.mat"
        last_el_edges = path_lst_edges[-1][0:-4] + "-edges.mat"
        last_el_frontNodeIds = path_lst_frontNodeIds[-1][0:-4] + "-frontIds.mat"
        last_el_backNodeIds = path_lst_backNodeIds[-1][0:-4] + "-backIds.mat"

        path_lst_ids[-1] = last_el_ids
        path_lst_pts[-1] = last_el_pts
        path_lst_edges[-1] = last_el_edges
        path_lst_frontNodeIds[-1] = last_el_frontNodeIds
        path_lst_backNodeIds[-1] = last_el_backNodeIds

        save_path_ids = '/'.join(path_lst_ids)
        save_path_pts = '/'.join(path_lst_pts)
        save_path_edges = '/'.join(path_lst_edges)
        save_path_frontNodeIds = '/'.join(path_lst_frontNodeIds)
        save_path_backNodeIds = '/'.join(path_lst_backNodeIds)

        sio.savemat(save_path_ids,{'ls_ids': ls_ids},oned_as='row')
        sio.savemat(save_path_pts,{'ls_pts': ls_pts},oned_as='row')
        sio.savemat(save_path_edges,{'edges': edges},oned_as='row')
        sio.savemat(save_path_frontNodeIds,{'ls_frontNode_ids': ls_frontNode_ids},oned_as='row')
        sio.savemat(save_path_backNodeIds,{'ls_backNode_ids': ls_backNode_ids},oned_as='row')

if __name__ == '__main__':
    # org = (42.34,-71.03)
    # proc = procNuScenes("Data/nuScenes2Lanelet/boston-seaport.osm",org)
    org = (1.32,103.79)
    # proc = procNuScenes("Data/nuScenes2Lanelet/singapore-hollandvillage.osm",org)
    # proc = procNuScenes("Data/nuScenes2Lanelet/singapore-onenorth.osm",org)
    proc = procNuScenes("Data/nuScenes2Lanelet/singapore-queenstown.osm",org)
    proc.process()