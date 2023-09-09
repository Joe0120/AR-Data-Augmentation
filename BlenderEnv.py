import bpy, os

class BlenderEnv:
    def __init__(self, config_setting):
        self.config_setting = config_setting

    def remove_all_obj(self):
        for obj in bpy.data.objects:
            if obj.name not in ['Camera', 'Light']:
                bpy.data.objects.remove(obj)
        for collection in bpy.data.collections:
            if collection.name not in ['Collection', 'fbx_col', 'blend_col']:
                bpy.data.collections.remove(collection)
        bpy.ops.outliner.orphans_purge(do_recursive=True)


    def set_env(self):
        bpy.context.scene.render.resolution_x = self.config_setting["blender_env"]["resolution"][0] #1280
        bpy.context.scene.render.resolution_y = self.config_setting["blender_env"]["resolution"][1] #720
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.view_layers["ViewLayer"].use_pass_object_index = True
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
        bpy.context.preferences.addons["cycles"].preferences.get_devices()

    def init_node(self):
        bpy.context.scene.render.film_transparent = True

        # set node tree
        bpy.data.scenes["Scene"].use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links
        for node in tree.nodes: 
            tree.nodes.remove(node)

        image_node = tree.nodes.new(type='CompositorNodeImage')
        image_node.image = bpy.data.images.load(os.path.abspath(self.config_setting["file_env"]["bg_path"]))
        # image_scale_node = tree.nodes.new(type='CompositorNodeScale')
        # image_scale_node.space = 'RENDER_SIZE'

        render_node = tree.nodes.new(type='CompositorNodeRLayers')
        # render_scale_node = tree.nodes.new(type='CompositorNodeScale')
        # render_scale_node.space = 'RENDER_SIZE'

        # alpha_over_node = tree.nodes.new(type='CompositorNodeAlphaOver')
        composite_node = tree.nodes.new(type='CompositorNodeComposite')

        # if self.config_setting["mode_config"]["with_bg"]:
        #     links.new(image_node.outputs[0], image_scale_node.inputs[0])
        #     links.new(render_node.outputs[0], render_scale_node.inputs[0])
        #     links.new(image_scale_node.outputs[0], alpha_over_node.inputs[1])
        #     links.new(render_scale_node.outputs[0], alpha_over_node.inputs[2])
        #     if self.config_setting["mode_config"]["with_color"]:
        #         # with background and color
        #         links.new(alpha_over_node.outputs[0], composite_node.inputs[0])
        #     else:
        #         # with background and no color
        #         color_ramp_node = tree.nodes.new(type='CompositorNodeValToRGB')
        #         links.new(alpha_over_node.outputs[0], color_ramp_node.inputs[0])
        #         links.new(color_ramp_node.outputs[0], composite_node.inputs[0])
        # else:
        #     # no background
        #     links.new(render_node.outputs[0], composite_node.inputs[0])
        links.new(render_node.outputs[0], composite_node.inputs[0])
