import math

class CameraModel:
    def __init__(self, frame_width, frame_height, field_of_view_x, camera_matrix, dist_coeffs, new_camera_matrix):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.field_of_view_x = field_of_view_x
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.new_camera_matrix = new_camera_matrix
        self.principal_point_x = camera_matrix[0][2]
        self.principal_point_y = camera_matrix[1][2]
        
    def _calc_angle(self, pixels_from_center):
        return math.atan(pixels_from_center * math.tan(self.field_of_view_x / 2) / (self.frame_width / 2))

    def px2meters(self, x, y, altitude, pitch=0, roll=0):
        x_from_principal_point = x - self.principal_point_x
        y_from_principal_point = y - self.principal_point_y
        
        x_angle = -self._calc_angle(x_from_principal_point) + pitch
        y_angle =  self._calc_angle(y_from_principal_point) + roll
        
        x_meters_from_center = -altitude * math.tan(x_angle)
        y_meters_from_center =  altitude * math.tan(y_angle)
        
        return x_meters_from_center, y_meters_from_center
