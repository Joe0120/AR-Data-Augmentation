import bpy, math, re
from mathutils import Matrix
from typing import Union
import numpy as np

class Camera:
    def __init__(self, config_setting):
        self.config_setting = config_setting
        self.location = {"x":None, "y":None, "z":None}
        self.rotation = {"x":None, "y":None, "z":None}
        self.kitti_calib = {"P0":None, "P1":None, "P2":None, "P3":None, "R0_rect":None, "Tr_velo_to_cam":None, "Tr_imu_to_velo":None}
        self.intrinsics = None

    def set_camera(self):
        if self.config_setting["blender_env"]["cam_location"]:
            for _idx, key in enumerate(self.location):
                self.location[key] = self.config_setting["blender_env"]["cam_location"][_idx]
                bpy.data.objects['Camera'].location[_idx] = self.config_setting["blender_env"]["cam_location"][_idx]
        else:
            for _idx, key in enumerate(self.location):
                self.location[key] = bpy.data.objects['Camera'].location[_idx]

        if self.config_setting["blender_env"]["cam_rotation"]:
            for _idx, key in enumerate(self.rotation):
                self.rotation[key] = self.config_setting["blender_env"]["cam_rotation"][_idx]
                bpy.data.objects['Camera'].rotation_euler[_idx] = math.radians(self.config_setting["blender_env"]["cam_rotation"][_idx])
        else:
            for _idx, key in enumerate(self.rotation):
                self.rotation[key] = math.degrees(bpy.data.objects['Camera'].rotation_euler[_idx])

        bpy.data.objects['Camera'].data.clip_end = self.config_setting["blender_env"]["cam_distance"]
        if self.config_setting["mode_config"]["is_fisheye"]:
            bpy.data.objects['Camera'].data.type = 'PANO'
            bpy.data.objects['Camera'].data.cycles.panorama_type = 'FISHEYE_EQUISOLID'

        if self.config_setting["file_env"]["kitti_calib_file"]:
            with open(self.config_setting["file_env"]["kitti_calib_file"], encoding="utf-8") as txt_file:
                content = txt_file.read()
            for key in self.kitti_calib:
                self.kitti_calib[key] = re.search(f'{key}: ([\d\ \.e\+\-]*)', content).group(1)

            P2_float_calib = [float(value) for value in self.kitti_calib["P2"].split()]
            P2_np_calib = np.array(P2_float_calib).reshape(3, 4)[:, :3]

            self.set_intrinsics_from_K_matrix(P2_np_calib, self.config_setting["blender_env"]["resolution"][0], self.config_setting["blender_env"]["resolution"][1])
            self.intrinsics = self.get_intrinsics_as_K_matrix()

            P2_kitti = np.array([np.append(row, 0) for row in self.intrinsics]).flatten()
            self.kitti_calib["P2"] = ' '.join(map(str, P2_kitti))

        if self.config_setting["blender_env"]["cam_intrinsics"]:
            self.set_intrinsics_from_K_matrix(np.array(self.config_setting["blender_env"]["cam_intrinsics"]), self.config_setting["blender_env"]["resolution"][0], self.config_setting["blender_env"]["resolution"][1])
            self.intrinsics = self.get_intrinsics_as_K_matrix()
            P2_kitti = np.array([np.append(row, 0) for row in self.intrinsics]).flatten()
            self.kitti_calib["P2"] = ' '.join(map(str, P2_kitti))


    def get_intrinsics_as_K_matrix(self) -> np.ndarray:
        """ Returns the current set intrinsics in the form of a K matrix.

        This is basically the inverse of the the set_intrinsics_from_K_matrix() function.

        :return: The 3x3 K matrix
        """
        cam_ob = bpy.context.scene.camera
        cam = cam_ob.data

        f_in_mm = cam.lens
        resolution_x_in_px = bpy.context.scene.render.resolution_x
        resolution_y_in_px = bpy.context.scene.render.resolution_y

        # Compute sensor size in mm and view in px
        pixel_aspect_ratio = bpy.context.scene.render.pixel_aspect_y / bpy.context.scene.render.pixel_aspect_x
        view_fac_in_px = self.get_view_fac_in_px(cam, bpy.context.scene.render.pixel_aspect_x,
                                            bpy.context.scene.render.pixel_aspect_y, resolution_x_in_px, resolution_y_in_px)
        sensor_size_in_mm = self.get_sensor_size(cam)

        # Convert focal length in mm to focal length in px
        fx = f_in_mm / sensor_size_in_mm * view_fac_in_px
        fy = fx / pixel_aspect_ratio

        # Convert principal point in blenders format to px
        cx = (resolution_x_in_px - 1) / 2 - cam.shift_x * view_fac_in_px
        cy = (resolution_y_in_px - 1) / 2 + cam.shift_y * view_fac_in_px / pixel_aspect_ratio

        # Build K matrix
        K = np.array([[fx, 0, cx],
                    [0, fy, cy],
                    [0, 0, 1]])
        return K

    def get_view_fac_in_px(self, cam: bpy.types.Camera, pixel_aspect_x: float, pixel_aspect_y: float,
                        resolution_x_in_px: int, resolution_y_in_px: int) -> int:
        """ Returns the camera view in pixels.

        :param cam: The camera object.
        :param pixel_aspect_x: The pixel aspect ratio along x.
        :param pixel_aspect_y: The pixel aspect ratio along y.
        :param resolution_x_in_px: The image width in pixels.
        :param resolution_y_in_px: The image height in pixels.
        :return: The camera view in pixels.
        """
        # Determine the sensor fit mode to use
        if cam.sensor_fit == 'AUTO':
            if pixel_aspect_x * resolution_x_in_px >= pixel_aspect_y * resolution_y_in_px:
                sensor_fit = 'HORIZONTAL'
            else:
                sensor_fit = 'VERTICAL'
        else:
            sensor_fit = cam.sensor_fit

        # Based on the sensor fit mode, determine the view in pixels
        pixel_aspect_ratio = pixel_aspect_y / pixel_aspect_x
        if sensor_fit == 'HORIZONTAL':
            view_fac_in_px = resolution_x_in_px
        else:
            view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px

        return view_fac_in_px

    def get_sensor_size(self, cam: bpy.types.Camera) -> float:
        """ Returns the sensor size in millimeters based on the configured sensor_fit.

        :param cam: The camera object.
        :return: The sensor size in millimeters.
        """
        if cam.sensor_fit == 'VERTICAL':
            sensor_size_in_mm = cam.sensor_height
        else:
            sensor_size_in_mm = cam.sensor_width
        return sensor_size_in_mm

    def set_intrinsics_from_K_matrix(self, K: Union[np.ndarray, Matrix], image_width: int, image_height: int,
                                    clip_start: float = None, clip_end: float = None):
        """ Set the camera intrinsics via a K matrix.

        The K matrix should have the format:
            [[fx, 0, cx],
            [0, fy, cy],
            [0, 0,  1]]

        This method is based on https://blender.stackexchange.com/a/120063.

        :param K: The 3x3 K matrix.
        :param image_width: The image width in pixels.
        :param image_height: The image height in pixels.
        :param clip_start: Clipping start.
        :param clip_end: Clipping end.
        """

        K = Matrix(K)

        cam = bpy.context.scene.camera.data

        if abs(K[0][1]) > 1e-7:
            raise ValueError(f"Skew is not supported by blender and therefore "
                            f"not by BlenderProc, set this to zero: {K[0][1]} and recalibrate")

        fx, fy = K[0][0], K[1][1]
        cx, cy = K[0][2], K[1][2]

        # If fx!=fy change pixel aspect ratio
        pixel_aspect_x = pixel_aspect_y = 1
        if fx > fy:
            pixel_aspect_y = fx / fy
        elif fx < fy:
            pixel_aspect_x = fy / fx

        # Compute sensor size in mm and view in px
        pixel_aspect_ratio = pixel_aspect_y / pixel_aspect_x
        view_fac_in_px = self.get_view_fac_in_px(cam, pixel_aspect_x, pixel_aspect_y, image_width, image_height)
        sensor_size_in_mm = self.get_sensor_size(cam)

        # Convert focal length in px to focal length in mm
        f_in_mm = fx * sensor_size_in_mm / view_fac_in_px

        # Convert principal point in px to blenders internal format
        shift_x = (cx - (image_width - 1) / 2) / -view_fac_in_px
        shift_y = (cy - (image_height - 1) / 2) / view_fac_in_px * pixel_aspect_ratio

        # Finally set all intrinsics
        self.set_intrinsics_from_blender_params(f_in_mm, image_width, image_height, clip_start, clip_end, pixel_aspect_x,
                                        pixel_aspect_y, shift_x, shift_y, "MILLIMETERS")

    def set_intrinsics_from_blender_params(self, lens: float = None, image_width: int = None, image_height: int = None,
                                        clip_start: float = None, clip_end: float = None,
                                        pixel_aspect_x: float = None, pixel_aspect_y: float = None, shift_x: int = None,
                                        shift_y: int = None, lens_unit: str = None):
        """ Sets the camera intrinsics using blenders represenation.

        :param lens: Either the focal length in millimeters or the FOV in radians, depending on the given lens_unit.
        :param image_width: The image width in pixels.
        :param image_height: The image height in pixels.
        :param clip_start: Clipping start.
        :param clip_end: Clipping end.
        :param pixel_aspect_x: The pixel aspect ratio along x.
        :param pixel_aspect_y: The pixel aspect ratio along y.
        :param shift_x: The shift in x direction.
        :param shift_y: The shift in y direction.
        :param lens_unit: Either FOV or MILLIMETERS depending on whether the lens is defined as focal length in
                        millimeters or as FOV in radians.
        """

        cam_ob = bpy.context.scene.camera
        cam = cam_ob.data

        if lens_unit is not None:
            cam.lens_unit = lens_unit

        if lens is not None:
            # Set focal length
            if cam.lens_unit == 'MILLIMETERS':
                if lens < 1:
                    raise Exception("The focal length is smaller than 1mm which is not allowed in blender: " + str(lens))
                cam.lens = lens
            elif cam.lens_unit == "FOV":
                cam.angle = lens
            else:
                raise Exception("No such lens unit: " + lens_unit)

        # Set resolution
        if image_width is not None:
            bpy.context.scene.render.resolution_x = image_width
        if image_height is not None:
            bpy.context.scene.render.resolution_y = image_height

        # Set clipping
        if clip_start is not None:
            cam.clip_start = clip_start
        if clip_end is not None:
            cam.clip_end = clip_end

        # Set aspect ratio
        if pixel_aspect_x is not None:
            bpy.context.scene.render.pixel_aspect_x = pixel_aspect_x
        if pixel_aspect_y is not None:
            bpy.context.scene.render.pixel_aspect_y = pixel_aspect_y

        # Set shift
        if shift_x is not None:
            cam.shift_x = shift_x
        if shift_y is not None:
            cam.shift_y = shift_y
