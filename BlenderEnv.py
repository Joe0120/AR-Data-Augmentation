import bpy, os

class BlenderEnv:
    def __init__(self, config_setting):
        self.config_setting = config_setting

    def remove_all_obj(self):
        for obj in bpy.data.objects:
            if obj.name not in ['Camera', 'Light', 'Sun']:
                bpy.data.objects.remove(obj)
        for collection in bpy.data.collections:
            if collection.name not in ['Collection', 'fbx_col', 'blend_col']:
                bpy.data.collections.remove(collection)
        bpy.ops.outliner.orphans_purge(do_recursive=True)

    def set_env(self):
        bpy.context.scene.render.resolution_x = self.config_setting["blender_env"]["resolution"][0] #1280
        bpy.context.scene.render.resolution_y = self.config_setting["blender_env"]["resolution"][1] #720
        bpy.context.scene.render.resolution_percentage = 100
        if self.config_setting["file_env"]["blender_file"]:
            bpy.context.scene.view_layers["View Layer"].use_pass_object_index = True
        else:
            bpy.context.scene.view_layers["ViewLayer"].use_pass_object_index = True
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
        bpy.context.preferences.addons["cycles"].preferences.get_devices()

    def create_collection(self):
        for name in ['fbx_col', 'blend_col']:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
        return

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
        render_node = tree.nodes.new(type='CompositorNodeRLayers')
        composite_node = tree.nodes.new(type='CompositorNodeComposite')
        links.new(render_node.outputs[0], composite_node.inputs[0])

    def render(self, file_path):
        bpy.context.scene.render.filepath = file_path
        bpy.ops.render.render(write_still=True)