def st_buffer_squashed(linestring, buffer_radius, end_cap_radius):
    import numpy as np
    import shapely
    from shapely.geometry import LineString
    from shapely.geometry import Point
    from shapely.geometry import Polygon
    
    import warnings
    if end_cap_radius > buffer_radius:
        warnings.warn("end_cap_radius > buffer_radius. Truncating end_cap_radius", UserWarning)
        end_cap_radius = buffer_radius
    if end_cap_radius < 0:
        warnings.warn("end_cap_radius < 0. Returning flat cap buffer", UserWarning)
        return linestring.buffer(buffer_radius, cap_style='flat')
    
    
    first_two_points = list(linestring.coords[:2])
    line_first_two_points = LineString(first_two_points)
    first_two_x, first_two_y = line_first_two_points.xy
    
    last_two_points = list(linestring.coords[-2:])
    line_last_two_points = LineString(last_two_points)
    last_two_x, last_two_y = line_last_two_points.xy
    
    ### handle inf slope
    if first_two_x[1] == first_two_x[0]:
        first_two_x[1] += 0.000001
    if last_two_x[1] == last_two_x[0]:
        last_two_x[1] += 0.000001
        
    first_two_slope = (first_two_y[1] - first_two_y[0])/(first_two_x[1] - first_two_x[0])
    last_two_slope = (last_two_y[1] - last_two_y[0])/(last_two_x[1] - last_two_x[0])

    cap_buffer_ratio = end_cap_radius / buffer_radius
    
    ### distance to move off from first point or last point to get center of circle
    circle_center_distance = (1-cap_buffer_ratio**2)/(2*cap_buffer_ratio) * buffer_radius
    ### radius of circle that will define squashed end
    circle_radius = np.sqrt(circle_center_distance**2 + buffer_radius**2)
    
    start_posn_delta_x = np.sqrt(circle_center_distance**2 / (1 + first_two_slope**2))
    if first_two_x[1] < first_two_x[0]:
        start_posn_delta_x *= -1
    start_posn_delta_y = first_two_slope * start_posn_delta_x

    end_posn_delta_x = np.sqrt(circle_center_distance**2 / (1 + last_two_slope**2))
    if last_two_x[1] < last_two_x[0]:
        end_posn_delta_x *= -1
    end_posn_delta_y = last_two_slope * end_posn_delta_x

    start_circle_x_center = first_two_x[0] + start_posn_delta_x
    start_circle_y_center = first_two_y[0] + start_posn_delta_y

    end_circle_x_center = last_two_x[1] - end_posn_delta_x
    end_circle_y_center = last_two_y[1] - end_posn_delta_y
    
    start_circle_center = Point(start_circle_x_center, start_circle_y_center)
    end_circle_center = Point(end_circle_x_center, end_circle_y_center)

    # Create a circular polygon using the buffer method
    start_circle = start_circle_center.buffer(circle_radius)
    end_circle = end_circle_center.buffer(circle_radius)
    
    ### st functions
    buffer_flat = linestring.buffer(buffer_radius, cap_style='flat')
    start_round = Point(first_two_x[0],first_two_y[0]).buffer(buffer_radius)
    end_round = Point(last_two_x[1],last_two_y[1]).buffer(buffer_radius)
    buffer_difference_start = start_round.difference(buffer_flat)
    buffer_difference_end = end_round.difference(buffer_flat)
    
    start_cap_squashed = buffer_difference_start.intersection(start_circle)
    end_cap_squashed = buffer_difference_end.intersection(end_circle)
    
    final_squashed_buffer = buffer_flat.union(start_cap_squashed).union(end_cap_squashed)
    return final_squashed_buffer